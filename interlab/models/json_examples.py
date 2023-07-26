import json

from ..context import with_context
from ..text.json_parsing import find_and_parse_json_block
from .query_engine import query_engine

_GENERATE_JSON_EXAMPLE_PROMPT = """\
Create a minimal example JSON object conforming to the following JSON schema:\n
```json
{schema}
```\n
Write exactly one example JSON object as a single markdown JSON code block delimited by "```json" and "```"."""

_GENERATE_JSON_DEFAULT_ENGINE = "gpt-3.5-turbo"


# TODO: add caching (on disk or at least in memory for the session)
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
