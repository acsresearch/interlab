import abc
from typing import Optional


class LangModelBase(abc.ABC):
    @abc.abstractmethod
    def prepare_conf(self, **kwargs) -> (str, dict[str, any]):
        raise NotImplementedError()

    @abc.abstractmethod
    def _query(self, prompt: str, conf: dict[str, any]) -> str:
        raise NotImplementedError()

    def query(self, prompt: str, max_tokens: Optional[int] = None, strip=True) -> str:
        return query_model(
            self, prompt, {"max_tokens": max_tokens, "strip": bool(strip)}
        )

    # Note: this is not an abstract method on purpose
    async def aquery(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        raise NotImplementedError()

    def __repr__(self):
        return f"{self.__class__.__name__}()"


from .query_model import query_model  # noqa: E402
