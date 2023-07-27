import asyncio
import logging
import os
from dataclasses import dataclass

import anthropic

from ..context import Context
from ..utils.text import group_newlines, remove_leading_spaces, shorten_str
from .base import LangModelBase, ModelConf

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

    def _prepare_inputs(self, prompt: str, max_tokens: int):
        conf = ModelConf(
            api="Anthropic",
            model=self.model,
            temperature=self.temperature,
            max_tokens=max_tokens,
        )
        inputs = {
            "prompt": prompt,
            "conf": conf,
        }
        return inputs

    def query(self, prompt: str, max_tokens=1024, strip=None) -> str:
        if strip is True:
            prompt = remove_leading_spaces(group_newlines(prompt.strip()))
        inputs = self._prepare_inputs(prompt, max_tokens)
        with Context(f"Anthropic {self.model}", inputs=inputs) as c:
            r = self.client.completions.create(
                prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
                stop_sequences=[anthropic.HUMAN_PROMPT],
                max_tokens_to_sample=max_tokens,
                temperature=self.temperature,
                model=self.model,
            )
            d = r.completion.strip()
            if strip is True:
                d = group_newlines(d.strip())
            c.set_result(d)
            return d

    async def aquery(self, prompt: str, max_tokens=1024) -> str:
        inputs = self._prepare_inputs(prompt, max_tokens)
        with Context(f"Anthropic {self.model}", inputs=inputs) as c:
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
