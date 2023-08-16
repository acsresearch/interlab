import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

import anthropic

from ..context import Context
from ..utils.text import group_newlines, remove_leading_spaces, shorten_str
from .base import LangModelBase

_LOG = logging.getLogger(__name__)

_anthropic_semaphore = asyncio.Semaphore(12)


@dataclass
class AnthropicModel(LangModelBase):
    model: str
    temperature: float

    def __init__(
        self, api_key: str = None, model="claude-v1", temperature: float = 1.0
    ):
        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            assert (
                api_key
            ), "need to provide either key param or ANTHROPIC_API_KEY env var"
        self.api_key = api_key
        self.client = anthropic.Client(api_key=self.api_key)
        self.aclient = anthropic.AsyncAnthropic(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        _LOG.info(
            f"Created {self.__class__.__name__} with API_KEY={shorten_str(self.api_key, 17)}, "
            f"default model={self.model}"
        )

    def prepare_conf(self, max_tokens: Optional[int], strip=True):
        if max_tokens is None:
            max_tokens = 1024
        typename = __class__.__qualname__
        name = f"query interlab {typename} ({self.model})"
        conf = {
            "model_name": self.model,
            "temperature": self.temperature,
            "max_tokens": max_tokens,
            "strip": strip,
        }
        return name, conf

    def _query(self, prompt: str, conf: dict[str, Any]) -> str:
        strip = conf["strip"]
        if strip is True:
            prompt = remove_leading_spaces(group_newlines(prompt.strip()))
        r = self.client.completions.create(
            prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
            stop_sequences=[anthropic.HUMAN_PROMPT],
            max_tokens_to_sample=conf["max_tokens"],
            temperature=conf["temperature"],
            model=conf["model_name"],
        )
        d = r.completion.strip()
        if strip is True:
            d = group_newlines(d.strip())
        return d

    async def aquery(self, prompt: str, max_tokens=1024) -> str:
        name, conf = self.prepare_conf(max_tokens, strip=True)
        with Context(name, inputs={"prompt": prompt, "conf": conf}) as c:
            async with _anthropic_semaphore:
                r = await self.aclient.completions.create(
                    prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
                    stop_sequences=[anthropic.HUMAN_PROMPT],
                    max_tokens_to_sample=max_tokens,
                    temperature=self.temperature,
                    model=self.model,
                )
                d = r.completion.strip()
                c.set_result(d)
                return d

    def __repr__(self):
        return f"{self.__class__.__name__}(model={self.model!r}, temperature={self.temperature!r})"
