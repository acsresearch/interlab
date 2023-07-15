import json
import re
from typing import TypeVar

import jsonref
import pydantic

from ..context import Context


_FORMAT_PROMPT = """\
# Instructions to format the answer:\n
{deliberation}Write your answer to the prompt as JSON conforming to the following JSON schema:\n
```
{schema}
```\n
Write the answer as JSON in a ```-delimited code block.
"""

_FORMAT_PROMPT_DELIBERATE = """\
First, write any thoughts or deliberation in free-form text.
"""

_FORMAT_PROMPT_EXAMPLE = """\
Here is an example JSON instance of the given schema.\n
```
{example}
```\n"""

_GET_EXAMPLE_PROMPT = """\
Create a minimal example JSON object conforming to the following JSON schema:\n
```
{schema}
```\n
Write exactly one example JSON object as JSON in a ```-delimited code block."""

_FORMAT_VAR = "FORMAT_PROMPT"

_JSON_REGEXP = re.compile("```(?:json)?\s*(\{.*\})\s*```", re.I | re.M | re.S)


# TODO: add caching (files or at least memory)
# TODO: switch to GPT-3.5 as the default model
def _get_json_example(json_schema: str, engine=None, max_repeats=5) -> str | None:
    if engine is None:
        import langchain

        engine = langchain.OpenAI(model_name="text-davinci-003")
    prompt = _GET_EXAMPLE_PROMPT.format(schema=json_schema)
    for i in range(max_repeats):
        res = engine(prompt)
        m = _JSON_REGEXP.search(res)
        if not m or len(m.groups()) != 1:
            continue
        try:
            d = json.loads(m.groups()[0])
            return json.dumps(d)
        except json.JSONDecodeError:
            pass
    return None


def _json_schema_and_type(T: type):
    if not isinstance(T, pydantic.BaseModel):
        T = pydantic.dataclasses.create_pydantic_model_from_dataclass(T)
    # pydantic schema
    schema = T.schema()
    # remove root title and description (usually misleading to LLMs in dataclasses)
    schema.pop("title", None)
    schema.pop("description", None)
    # dereference all $refs, keep the old ref when recursive types are encountered

    def recfix(a, seen=()):
        """Recursively replace JSONRefs with normal dicts, should behave ok for recursive types"""
        if isinstance(a, jsonref.JsonRef):
            assert isinstance(a, dict)
            if id(a) not in seen:
                return {k: recfix(v, seen + (id(a),)) for k, v in a.items()}
            else:
                return a
        if isinstance(a, dict):
            return {k: recfix(v, seen) for k, v in a.items()}
        if isinstance(a, list):
            return [recfix(v, seen) for v in a]
        return a

    schema_ref = jsonref.replace_refs(schema)
    schema_unref = recfix(schema_ref)

    # Try removing the definitions and see if jsonref is still happy to parse it, keep them otherwise
    try:
        schema_unref2 = dict(schema_unref)
        schema_unref2.pop("definitions", None)
        schema_str = jsonref.dumps(schema_unref2)
        repr(
            jsonref.loads(schema_str, lazy_load=False)
        )  # To check validity of $refs in schema
        return schema_str, T
    except jsonref.JsonRefError:
        pass

    return jsonref.dumps(schema_unref), T


TOut = TypeVar("TOut")


def query_json(
    engine: callable,
    T: type,
    prompt: str,
    with_example: bool | TOut | str = False,
    with_deliberation: bool | str = True,
    max_repeats: int = 5,
    example_engine=None,
) -> TOut:
    """
    TODO: Docs
    """
    # TODO: preserve and log any richer structure of the prompt into the context?
    prompt = str(prompt)
    if _FORMAT_VAR not in prompt:
        prompt += f"\n\n\n{'{'+_FORMAT_VAR+'}'}"

    deliberaion = ""
    if isinstance(with_deliberation, str):
        deliberaion = with_deliberation
    elif with_deliberation:
        deliberaion = _FORMAT_PROMPT_DELIBERATE

    schema, pdtT = _json_schema_and_type(T)
    format_prompt = _FORMAT_PROMPT.format(schema=schema, deliberation=deliberaion)

    if with_example is True:
        with_example = _get_json_example(schema, engine=example_engine)
    if with_example and not isinstance(with_example, str):
        with_example = json.dumps(with_example)
    if with_example:
        format_prompt += _FORMAT_PROMPT_EXAMPLE.format(example=with_example)

    prompt_with_fmt = prompt.format(**{_FORMAT_VAR: format_prompt})

    with Context(f"Querying {engine} for JSON of type {T}", kind="query_json") as c:
        c.add_input("prompt", prompt_with_fmt)
        for i in range(max_repeats):
            res = engine(prompt_with_fmt)
            m = _JSON_REGEXP.search(res)
            if not m or len(m.groups()) != 1:
                continue
            try:
                d = pdtT.parse_raw(m.groups()[0])
                d = T(**d.dict())
                assert isinstance(d, T)
                c.set_result(d)
                return d
            except (json.JSONDecodeError, pydantic.ValidationError) as e:
                if i == max_repeats - 1:
                    c.set_error(e)
                    raise e
