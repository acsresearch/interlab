import asyncio
import os

from dataclasses import dataclass
from typing import Type

import pytest

from interlab.llm.engines import AnthropicEngine, OpenAiChatEngine, QueryEngine
from interlab.utils.data import serialize_with_type


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


@pytest.mark.skipif(
    not all(os.getenv(key) for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]),
    reason="Requires API keys",
)
@pytest.mark.parametrize("engine", [AnthropicEngine, OpenAiChatEngine])
def test_query(engine: Type[QueryEngine]):
    engine = engine()
    output = engine.query("Hello", max_tokens=10)
    assert isinstance(output, str)
    assert output


@pytest.mark.skipif(
    not all(os.getenv(key) for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]),
    reason="Requires API keys",
)
@pytest.mark.parametrize("engine", [AnthropicEngine, OpenAiChatEngine])
async def test_aquery(engine: Type[QueryEngine]):
    engine = engine()
    output = engine.aquery("Hello", max_tokens=10)
    await output
    assert isinstance(output, str)
    assert output
