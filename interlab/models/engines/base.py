import abc
from dataclasses import dataclass
from typing import Optional

from ...context.data.data import Data


class QueryEngine(abc.ABC):
    @abc.abstractmethod
    def query(self, prompt: str, max_tokens: Optional[int]) -> Data:
        raise NotImplementedError()

    # Note: this is not an abstract method on purpose
    async def aquery(self, prompt: str, max_tokens: Optional[int]) -> Data:
        raise NotImplementedError()


@dataclass
class QueryConf:
    api: str
    model: str
    temperature: float
    max_tokens: int
