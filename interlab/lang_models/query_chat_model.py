from dataclasses import dataclass
from typing import Any, Sequence


from ..context import Context
from ..context.data import FormatStr
import abc


@dataclass
class BaseMessage(abc.ABC):
    content: str | FormatStr

    @abc.abstractmethod
    def to_lc_message(self):
        raise NotImplementedError


class AiMessage(BaseMessage):
    def to_lc_message(self):
        from langchain.schema import AIMessage

        return AIMessage(content=str(self.content))


class HumanMessage(BaseMessage):
    def to_lc_message(self):
        from langchain.schema import HumanMessage

        return HumanMessage(content=str(self.content))


class SystemMessage(BaseMessage):
    def to_lc_message(self):
        from langchain.schema import SystemMessage

        return SystemMessage(content=str(self.content))


def _prepare_model(
    model: Any,
    model_kwargs: dict = None,
    call_async: bool = False,
):
    from langchain.chat_models.base import BaseChatModel

    if call_async:
        raise NotImplementedError()
    if model_kwargs is None:
        model_kwargs = {}

    typename = model.__class__.__qualname__
    conf = {"class": f"{model.__class__.__module__}.{typename}"}
    if isinstance(model, BaseChatModel):
        conf.update(model.dict())
        if "model_name" not in conf:
            conf["model_name"] = getattr(model, "model", None)
        name = f"query langchain chat model {typename} ({conf['model_name']})"
        call = lambda messages: model(
            [m.to_lc_message() for m in messages], **model_kwargs
        )
    else:
        raise TypeError("query_chat_model now works only for langchain chat models")
    conf.update(**model_kwargs)
    return name, conf, call


def query_chat_model(
    model: Any, messages: Sequence[BaseMessage], kwargs: dict = None, with_context=True
) -> str:
    name, conf, call = _prepare_model(model, model_kwargs=kwargs, call_async=False)

    if not isinstance(messages, Sequence):
        raise TypeError("query_chat_model accepts list of messages")

    if with_context:
        with Context(
            name, kind="query", inputs=dict(messages=messages, conf=conf)
        ) as c:
            r = call(messages).content
            c.set_result(r)
            return r
    else:
        return call(messages).content
