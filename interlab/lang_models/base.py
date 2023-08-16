import abc
from typing import Any, Optional


class LangModelBase(abc.ABC):
    @abc.abstractmethod
    def prepare_conf(self, **kwargs) -> (str, dict[str, Any]):
        raise NotImplementedError()

    @abc.abstractmethod
    def _query(self, prompt: str, conf: dict[str, Any]) -> str:
        raise NotImplementedError()

    def query(self, prompt: str, max_tokens: Optional[int] = None, strip=True) -> str:
        from .query_model import query_model

        return query_model(
            self, prompt, {"max_tokens": max_tokens, "strip": bool(strip)}
        )

    # Note: this is not an abstract method on purpose
    async def aquery(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        raise NotImplementedError()

    def __repr__(self):
        return f"{self.__class__.__name__}()"
