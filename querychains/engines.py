import openai
import anthropic
import os

from .utils import LOG, shorten_str
from .context import Context

class QueryEngine:
    def query(self, prompt: str, temperature: float = None) -> str:
        raise NotImplementedError()

    async def achat(self, prompt: str, temperature: float = None) -> str:
        raise NotImplementedError()


class OpenAIEngine(QueryEngine):
    def __init__(self, api_key: str = None, api_org: str = None, model="gpt-3.5-turbo"):
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
            assert api_key, "need to provide either key param or OPENAI_API_KEY env var"
        self.api_key = api_key
        if not api_org:
            api_org = os.getenv("OPENAI_API_ORG")
        self.api_org = api_org
        self.model = model
        LOG.info(
            f"Created OpenAIEngine with API_KEY={shorten_str(self.api_key, 13)} and API_ORG={shorten_str(self.api_org, 14)}, default model={self.model}"
        )

    def test(self):
        openai.Model.list(api_key=self.api_key, organization=self.api_org)

    def query(self, prompt: str, temperature: float = None, max_tokens=1024) -> str:
        with Context(f"query-chat-{self.model}", input=prompt) as c:
            openai.api_key = self.api_key
            openai.organization = self.api_org
            r = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            m = r.choices[0].message
            assert m.role == "assistant"
            d = m.content.strip()
            c.set_result(d)
            return d


class AnthropicEngine(QueryEngine):
    def __init__(self, api_key: str = None, model="claude-v1"):
        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            assert (
                api_key
            ), "need to provide either key param or ANTHROPIC_API_KEY env var"
        self.api_key = api_key
        self.client = anthropic.Client(self.api_key)
        self.model = model
        LOG.info(
            f"Created AnthropicEngine with API_KEY={shorten_str(self.api_key, 17)}, default model={self.model}"
        )

    def query(self, prompt: str, temperature: float = 1.0, max_tokens=1024) -> str:
        with Context(f"query-chat-{self.model}", input=prompt) as c:
            r = self.client.completion(
                prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
                stop_sequences=[anthropic.HUMAN_PROMPT],
                max_tokens_to_sample=max_tokens,
                temperature=temperature,
                model=self.model,
            )
            d = r["completion"].strip()
            c.set_result(d)
            return d
