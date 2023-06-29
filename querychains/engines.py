import asyncio
import os
from dataclasses import dataclass
from typing import Optional

import anthropic
import backoff
import openai

from .context import Context
from .data import Data
from .text import group_newlines, remove_leading_spaces
from .utils import LOG, shorten_str

# Time window when queries qill be retried on service or network failures
# Note that this does not limit the time of the last query itself
MAX_QUERY_TIME = 120
BACKOFF_EXCEPTIONS = (openai.error.RateLimitError, openai.error.ServiceUnavailableError)


class QueryEngine:
    def query(self, prompt: str, max_tokens: Optional[int]) -> Data:
        raise NotImplementedError()

    async def aquery(self, prompt: str, max_tokens: Optional[int]) -> Data:
        raise NotImplementedError()


@dataclass
class QueryConf:
    api: str
    model: str
    temperature: float
    max_tokens: int


_openai_semaphore = asyncio.Semaphore(12)
_anthropic_semaphore = asyncio.Semaphore(12)


@backoff.on_exception(
    backoff.expo,
    BACKOFF_EXCEPTIONS,
    max_time=MAX_QUERY_TIME,
)
def _make_openai_chat_query(api_key: str, api_org: str, prompt, conf: QueryConf):
    # openai.api_key = api_key
    # openai.organization = api_org
    r = openai.ChatCompletion.create(
        api_key=api_key,
        organization=api_org,
        model=conf.model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=conf.max_tokens,
        temperature=conf.temperature,
    )
    m = r.choices[0].message
    assert m.role == "assistant"
    return m.content.strip()


@backoff.on_exception(
    backoff.expo,
    BACKOFF_EXCEPTIONS,
    max_time=MAX_QUERY_TIME,
)
async def _make_openai_chat_async_query(
    api_key: str, api_org: str, prompt, conf: QueryConf
):
    r = await openai.ChatCompletion.acreate(
        api_key=api_key,
        organization=api_org,
        model=conf.model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=conf.max_tokens,
        temperature=conf.temperature,
    )
    m = r.choices[0].message
    assert m.role == "assistant"
    return m.content.strip()


@dataclass
class OpenAiChatEngine(QueryEngine):
    model: str
    temperature: float

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_org: Optional[str] = None,
        model="gpt-3.5-turbo",
        temperature: float = 0.7,
    ):
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
            assert api_key, "need to provide either key param or OPENAI_API_KEY env var"
        self.api_key = api_key
        if not api_org:
            api_org = os.getenv("OPENAI_API_ORG")
        self.api_org = api_org
        self.model = model
        LOG.info(
            f"Created OpenAIEngine with API_KEY={shorten_str(self.api_key, 13)} and "
            f"API_ORG={shorten_str(self.api_org, 14)}, model={self.model}"
        )
        self.temperature = temperature

    def test(self):
        openai.Model.list(api_key=self.api_key, organization=self.api_org)

    def _prepare_inputs(self, prompt, max_tokens):
        conf = QueryConf(
            api="OpenAiChat",
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
        with Context(f"OpenAiChat {self.model}", kind="query", inputs=inputs) as c:
            result = _make_openai_chat_query(
                self.api_key, self.api_org, prompt, inputs["conf"]
            )

            if strip is True:
                result = group_newlines(result.strip())
            c.set_result(result)
            return result

    async def aquery(self, prompt: str, max_tokens=1024) -> str:
        inputs = self._prepare_inputs(prompt, max_tokens)
        with Context(f"OpenAiChat {self.model}", kind="query", inputs=inputs) as c:
            async with _openai_semaphore:  # !!!  acquire semaphore outside of @backoff function is intensional
                result = await _make_openai_chat_async_query(
                    self.api_key, self.api_org, prompt, inputs["conf"]
                )
            c.set_result(result)
            return result


@dataclass
class AnthropicEngine(QueryEngine):
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
        self.client = anthropic.Client(self.api_key)
        self.model = model
        self.temperature = temperature
        LOG.info(
            f"Created AnthropicEngine with API_KEY={shorten_str(self.api_key, 17)}, default model={self.model}"
        )

    def _prepare_inputs(self, prompt: str, max_tokens: int):
        conf = QueryConf(
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
            r = self.client.completion(
                prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
                stop_sequences=[anthropic.HUMAN_PROMPT],
                max_tokens_to_sample=max_tokens,
                temperature=self.temperature,
                model=self.model,
            )
            d = r["completion"].strip()
            if strip is True:
                d = group_newlines(d.strip())
            c.set_result(d)
            return d

    async def aquery(self, prompt: str, max_tokens=1024) -> str:
        inputs = self._prepare_inputs(prompt, max_tokens)
        with Context(f"Anthropic {self.model}", inputs=inputs) as c:
            async with _anthropic_semaphore:
                r = await self.client.acompletion(
                    prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
                    stop_sequences=[anthropic.HUMAN_PROMPT],
                    max_tokens_to_sample=max_tokens,
                    temperature=self.temperature,
                    model=self.model,
                )
                d = r["completion"].strip()
                c.set_result(d)
                return d
