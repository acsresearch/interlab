import json
import re
from typing import Optional, TypeVar

import jsonref
import pydantic

from ..context import Context, with_context
from .engine_wrapping import query_engine
from .json_parsing import (
    JSON,
    find_and_parse_json_block,
    into_pydantic_model,
    json_schema,
)

_GENERATE_JSON_EXAMPLE_PROMPT = """\
Create a minimal example JSON object conforming to the following JSON schema:\n
```json
{schema}
```\n
Write exactly one example JSON object as a single markdown JSON code block delimited by "```json" and "```"."""

_GENERATE_JSON_DEFAULT_ENGINE = "gpt-3.5-turbo"


# TODO: add caching (files or at least memory)
# TODO: switch to GPT-3.5 as the default model
def generate_json_example(json_schema: JSON, engine=None, max_repeats=3) -> JSON | None:
    """
    Uses the given engine (or gpt-3.5-turbo by default) to generate a single example JSON for the given schema.

    Returns the example as JSON object, or None upon repeated failure.
    """
    if engine is None:
        import langchain.chat_models

        engine = langchain.chat_models.ChatOpenAI(
            model_name=_GENERATE_JSON_DEFAULT_ENGINE, max_tokens=2000
        )
    prompt = _GENERATE_JSON_EXAMPLE_PROMPT.format(schema=json.dumps(json_schema))

    @with_context(name="generate example JSON for JSON schema", kind="query")
    def generate_json_example_inner(_schema):
        for i in range(max_repeats):
            res = query_engine(engine, prompt)
            try:
                return find_and_parse_json_block(res)
            except ValueError:
                pass
        return None

    return generate_json_example_inner(json_schema)


_FORMAT_PROMPT = """\
# Instructions to format the answer:\n
{deliberation}Write your answer to the prompt as a single JSON conforming to the following JSON schema:\n
```json
{schema}
```\n
The answer should be written as a single markdown JSON code block delimited by "```json" and "```".
"""

_FORMAT_PROMPT_DELIBERATE = """\
First, write any thoughts or deliberation as free-form text containing no JSON.
"""

_FORMAT_PROMPT_EXAMPLE = """\
Here is an example JSON instance of the given schema.\n
```json
{example}
```\n"""


_FORMAT_VAR = "FORMAT_PROMPT"

TOut = TypeVar("TOut")


def query_for_json(
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

    pdT = into_pydantic_model(T)
    schema = json_schema(pdT)
    format_prompt = _FORMAT_PROMPT.format(schema=schema, deliberation=deliberaion)

    if with_example is True:
        with_example = generate_json_example(schema, engine=example_engine)
    if with_example and not isinstance(with_example, str):
        with_example = json.dumps(with_example)
    if with_example:
        format_prompt += _FORMAT_PROMPT_EXAMPLE.format(example=with_example)

    prompt_with_fmt = prompt.format(**{_FORMAT_VAR: format_prompt})

    with Context(f"query for JSON of type {T}", kind="query") as c:
        c.add_input("prompt", prompt_with_fmt)
        for i in range(max_repeats):
            res = query_engine(engine, prompt_with_fmt)
            assert isinstance(res, str)
            try:
                d = find_and_parse_json_block(res)
                # TODO: Is the following conversion/validation working for nested fields as well?
                # Convert to pydantic type for permissive conversion and validation
                d = pdT(**d)
                # Convert back to match expected type (nested types are ok)
                d = T(**d.dict())
                assert isinstance(d, T)
                c.set_result(d)
                return d
            except (json.JSONDecodeError, ValueError, pydantic.ValidationError) as e:
                if i < max_repeats - 1:
                    continue
                # Errors on last turn get logged into context and propagated
                raise e
