from dataclasses import dataclass

from interlab import AnthropicEngine, OpenAiChatEngine
from interlab.context.data import serialize_with_type


def test_serialize_engines():
    @dataclass
    class Engines:
        first: AnthropicEngine
        second: OpenAiChatEngine

    engines = Engines(
        AnthropicEngine(api_key="xxx"), OpenAiChatEngine(api_key="xxx", api_org="yyy")
    )
    output = serialize_with_type(engines)
    assert output == {
        "first": {"model": "claude-v1", "temperature": 1.0},
        "second": {"model": "gpt-3.5-turbo", "temperature": 0.7},
        "_type": "Engines",
    }
    output = serialize_with_type(engines.first)
    assert output == {
        "model": "claude-v1",
        "temperature": 1.0,
        "_type": "AnthropicEngine",
    }
