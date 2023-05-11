import os
from dataclasses import dataclass
from typing import Optional

import anthropic
import backoff
import openai

from .context import Context
from .data import Data
from .utils import LOG, shorten_str


class QueryEngine:
    def query(self, prompt: str) -> Data:
        raise NotImplementedError()

    async def aquery(self, prompt: str) -> Data:
        raise NotImplementedError()


@dataclass
class QueryConf:
    api: str
    model: str
    temperature: float
    max_tokens: int


@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
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


class OpenAiEngine(QueryEngine):
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
            "API_ORG={shorten_str(self.api_org, 14)}, default model={self.model}"
        )
        self.temperature = temperature

    def test(self):
        openai.Model.list(api_key=self.api_key, organization=self.api_org)

    def query(self, prompt: str, max_tokens=1024) -> str:
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

        with Context(f"OpenAiChat {self.model}", kind="query", inputs=inputs) as c:
            result = _make_openai_chat_query(self.api_key, self.api_org, prompt, conf)
            c.set_result(result)
            return result


class AnthropicEngine(QueryEngine):
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

    def query(self, prompt: str, max_tokens=1024) -> str:
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
        with Context(f"Anthropic {self.model}", inputs=inputs) as c:
            r = self.client.completion(
                prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
                stop_sequences=[anthropic.HUMAN_PROMPT],
                max_tokens_to_sample=max_tokens,
                temperature=self.temperature,
                model=self.model,
            )
            d = r["completion"].strip()
            c.set_result(d)
            return d
