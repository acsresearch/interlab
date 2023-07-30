import abc
from dataclasses import dataclass
from typing import Optional

from ..context.serialization import Data


class LangModelBase(abc.ABC):
    @abc.abstractmethod
    def query(self, prompt: str, max_tokens: Optional[int]) -> Data:
        raise NotImplementedError()

    # Note: this is not an abstract method on purpose
    async def aquery(self, prompt: str, max_tokens: Optional[int]) -> Data:
        raise NotImplementedError()

    def __repr__(self):
        return f"{self.__class__.__name__}()"


@dataclass
class ModelConf:
    api: str
    model: str
    temperature: float
    max_tokens: int
