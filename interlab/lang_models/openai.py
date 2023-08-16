import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

import backoff
import openai

from ..context import Context
from ..utils.text import group_newlines, remove_leading_spaces, shorten_str
from .base import LangModelBase

_LOG = logging.getLogger(__name__)

_openai_semaphore = asyncio.Semaphore(12)

# Time window when queries qill be retried on service or network failures
# Note that this does not limit the time of the last query itself
MAX_QUERY_TIME = 120
BACKOFF_EXCEPTIONS = (
    openai.error.RateLimitError,
    openai.error.ServiceUnavailableError,
    openai.error.APIError,
)


@backoff.on_exception(
    backoff.expo,
    BACKOFF_EXCEPTIONS,
    max_time=MAX_QUERY_TIME,
)
def _make_openai_chat_query(api_key: str, api_org: str, prompt, conf: dict[str, Any]):
    # openai.api_key = api_key
    # openai.organization = api_org
    r = openai.ChatCompletion.create(
        api_key=api_key,
        organization=api_org,
        model=conf["model_name"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=conf["max_tokens"],
        temperature=conf["temperature"],
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
    api_key: str, api_org: str, prompt, conf: dict[str, Any]
):
    r = await openai.ChatCompletion.acreate(
        api_key=api_key,
        organization=api_org,
        model=conf["model_name"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=conf["max_tokens"],
        temperature=conf["temperature"],
    )
    m = r.choices[0].message
    assert m.role == "assistant"
    return m.content.strip()


@dataclass
class OpenAiChatModel(LangModelBase):
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
        _LOG.info(
            f"Created {self.__class__.__name__} with API_KEY={shorten_str(self.api_key, 13)} and "
            f"API_ORG={shorten_str(self.api_org, 14)}, model={self.model}"
        )
        self.temperature = temperature

    def test(self):
        openai.Model.list(api_key=self.api_key, organization=self.api_org)

    def prepare_conf(
        self, max_tokens: Optional[int], strip=True
    ) -> (str, dict[str, Any]):
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
        result = _make_openai_chat_query(self.api_key, self.api_org, prompt, conf)
        if strip is True:
            result = group_newlines(result.strip())
        return result

    async def aquery(self, prompt: str, max_tokens=1024) -> str:
        name, conf = self.prepare_conf(max_tokens, True)
        with Context(name, kind="query", inputs={"prompt": prompt, "conf": conf}) as c:
            async with _openai_semaphore:  # !!!  acquire semaphore outside of @backoff function is intensional
                result = await _make_openai_chat_async_query(
                    self.api_key, self.api_org, prompt, conf
                )
            c.set_result(result)
            return result

    def __repr__(self):
        return f"{self.__class__.__name__}(model={self.model!r}, temperature={self.temperature!r})"
