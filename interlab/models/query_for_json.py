import json
import re
from typing import TypeVar

import pydantic
from fastapi.encoders import jsonable_encoder

from ..context import Context, with_context
from ..text.json_parsing import find_and_parse_json_block
from ..text.json_schema import get_json_schema, get_pydantic_model
from .query_engine import query_engine

_GENERATE_JSON_EXAMPLE_PROMPT = """\
Create a minimal example JSON object conforming to the following JSON schema:\n
```json
{schema}
```\n
Write exactly one example JSON object as a single markdown JSON code block delimited by "```json" and "```"."""

_GENERATE_JSON_DEFAULT_ENGINE = "gpt-3.5-turbo"


# TODO: add caching (files or at least memory)
def generate_json_example(json_schema: dict, engine=None, max_repeats=3) -> dict | None:
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
The answer should contain exactly one markdown JSON code block delimited by "```json" and "```".
"""

_FORMAT_PROMPT_DELIBERATE = """\
1. Deliberate about the task at hand and write out your thoughts as free-form text containing no JSON.
2. """

_FORMAT_PROMPT_EXAMPLE = """\
Here is an example JSON instance of the given schema.\n
```json
{example}
```\n"""


_FORMAT_VAR = "FORMAT_PROMPT"

TOut = TypeVar("TOut")


def query_for_json(
    engine: any,
    T: type,
    prompt: str,
    with_example: bool | TOut | str = False,
    with_cot: bool = False,
    max_repeats: int = 5,
    example_engine=None,
) -> TOut:
    """
    Prompt `engine` to produce a JSON representation of type `T`, and return it parsed and validated.

    * `engine` can be a langchain normal or chat engine, a interlab engine, or just any callable
    * `T` needs to be a dataclass, a pydantic BaseModel, or a pydantic dataclass.
      While defining the classes, use field names and desciprions that will help the LLM fill in the data as you
      expect it. Recursive classes are not suported.
      After parsing, the models will also be validated.
    * `prompt` is any string query to the model. If `prompt` contains "{FORMAT_PROMPT}", it will be replaced with format
      instructions, the JSON schema and the optional JSON example. Otherwise this information will be appended
      at the end of the prompt (this seems to work well).
    * `with_example=True` will generate an example JSON instance of the type and its schema, and the example will
      be added to the prompt. Examples can help smaller LLMs or with more complex tasks but it is for now unclear
      how much they help larger models, and there is some chance they influence the answer.
      The example is generated by an LLM (default: gpt-3.5-turbo) so they are trying to be semantically menaningful
      instances of type T relative to field names and descriptions.
      In-memory and on-disk caching of the examples for schemas is TODO.
      You can also provide your own example by passing a JSON string or JSON-serializable object in `with_example`.
      Note that a provided example is not validated (TODO: validate it).
    * `with_cot=True` adds a minimal prompt for writing chain-of-thought reasoning before writing
      out the JSON response. This may improve response quality (via CoT deliberation) but has some risks:
      the models may include JSON in their deliberation (confusing the parser) or run out of token limit via
      lenghty deliberation.
    * `max_repeats` limits how many times will the model be queried before raising an exception -
      all models have some chance to fail to follow the instructions, and this gives them several chances.
      Repetition is triggered valid JSON is not found in the output or if it fails to validate
      against the schema or any validators in the dataclasses.
      Note there is no repetition on LLM engine failure (the engine is expected to take care of network faiures etc.).
    * `example_engine` can specify an engine to use to generate the example JSON. By default, `gpt-3.5-turbo` is used.

    Returns a valid instance of `T` or raises `ValueError` if all retries failed to find valid JSON.

    *Notes:*

    - Context logging: `query_for_json` logs one Context for its call, and uses `call_engine` which
      also logs Contexts for the LLM calls themselves by default.

    - Uses pydatinc under the hood to construction of JSON schemas, flexible conversion of types to schema,
      validation etc.

    - The prompts ask the LLMs to wrap the JSON in markdown-style codeblocks for additional robustness
      (e.g. against wild `{` or `}` somewhere in surrounding text, which is hard to avoid reliably.),
      and falls back to looking for the outermost `{}`-pair.
      This may still fail e.g. when talking about JSON in your task, or having the JSON answer
      contain "```" as substrings. While current version seems sufficient, there are TODOs for improvement.

    - The schema presented to LLM is reference-free; all `$ref`s from the JSON schema are resolved.
    """
    # TODO(visualization): allow some richer structure of the prompt and its parameters,
    #   preserve and log this structure of the prompt into the context formatting?
    prompt = str(prompt)
    fmt_count = len(re.findall(f'{"{"}{_FORMAT_VAR}{"}"}', prompt))
    if fmt_count > 1:
        raise ValueError(
            f'Multiple instances of {"{"}{_FORMAT_VAR}{"}"} found in prompt'
        )
    if fmt_count == 0:
        prompt += f'\n\n\n{"{"}{_FORMAT_VAR}{"}"}'

    deliberation = _FORMAT_PROMPT_DELIBERATE if with_cot else ""

    pdT = get_pydantic_model(T)
    schema = get_json_schema(pdT)
    format_prompt = _FORMAT_PROMPT.format(schema=schema, deliberation=deliberation)

    if with_example is True:
        with_example = generate_json_example(schema, engine=example_engine)
    if with_example and not isinstance(with_example, str):
        with_example = json.dumps(jsonable_encoder(with_example))
    if with_example:
        format_prompt += _FORMAT_PROMPT_EXAMPLE.format(example=with_example)

    prompt_with_fmt = prompt.replace(f'{"{"}{_FORMAT_VAR}{"}"}', format_prompt)

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
            except (ValueError, pydantic.ValidationError) as e:
                if i < max_repeats - 1:
                    continue
                # Errors on last turn get logged into context and propagated
                raise ValueError(
                    f"engine repeatedly returned a response without a valid JSON instance of {T.__class__.__name__}"
                ) from e