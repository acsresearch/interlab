"""
Helpers for determining the token-length of a string.
"""

from typing import Any

import anthropic
import cachetools

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.language_models.llms import BaseLLM
import tiktoken


@cachetools.cached(cache=cachetools.LRUCache(maxsize=32))
def _get_tiktoken_tokenizer_for_model(name: str):
    return tiktoken.encoding_for_model(name)


@cachetools.cached(
    cache=cachetools.LRUCache(maxsize=256), key=lambda t, m: (str(t), str(m)), info=True
)
def count_tokens(text: str, model: str | Any) -> int:
    """
    Returns the number of tokens in a string, given a model name or a known model class.

    Currently supported:
    - OpenAI and Anthropic models by name
    - langchain models (chat and non-chat)
    - interlab models
    """
    if isinstance(model, str):
        try:
            tokenizer = _get_tiktoken_tokenizer_for_model(model)
            return len(tokenizer.encode(text))
        except KeyError:
            pass
        if model.startswith("claude"):
            return anthropic.Anthropic().count_tokens(text)
        raise ValueError(f"Unknown model name {model!r}")

    if isinstance(model, (BaseLLM, BaseChatModel)):
        return model.get_num_tokens(text)

    raise TypeError(f"Unknown model class {model.__class__.__name__}")
