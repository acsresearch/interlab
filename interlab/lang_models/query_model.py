from typing import Any

from interlab.context.data.format_str import FormatStr

from ..context import Context
from .base import LangModelBase


def _prepare_model(model: Any, model_kwargs: dict = None, call_async: bool = False):
    import langchain
    import langchain.schema

    if call_async:
        raise NotImplementedError()
    if model_kwargs is None:
        model_kwargs = {}

    typename = model.__class__.__qualname__
    conf = {"class": f"{model.__class__.__module__}.{typename}"}
    if isinstance(model, langchain.llms.base.BaseLLM):
        conf.update(model.dict())
        # For Anthropic (and maube other) langchain models:
        if "model_name" not in conf:
            conf["model_name"] = getattr(model, "model", None)
        name = f"Query langchain model {typename} ({conf['model_name']})"
        call = lambda c: model(c, **model_kwargs)  # noqa: E731
    elif isinstance(model, langchain.chat_models.base.BaseChatModel):
        conf.update(model.dict())
        if "model_name" not in conf:
            conf["model_name"] = getattr(model, "model", None)
        name = f"query langchain chat model {typename} ({conf['model_name']})"
        call = lambda c: model(  # noqa: E731
            [langchain.schema.HumanMessage(content=c)], **model_kwargs
        ).content
    elif isinstance(model, LangModelBase):
        name, cfg = model.prepare_conf(**model_kwargs)
        conf.update(cfg)
        call = lambda c: model._query(c, conf)  # noqa: E731
    elif callable(model):
        if hasattr(model, "__qualname__"):
            name = f"query function {getattr(model, '__module__', '<unknown>')}.{model.__qualname__}"
        else:
            name = f"query model {model.__module__}.{model.__class__.__qualname__}"

        call = lambda c: model(c, **model_kwargs)  # noqa: E731
    else:
        raise TypeError(f"Can't wrap model of type {model.__class__}")
    conf.update(**model_kwargs)
    return name, conf, call


def query_model(
    model: Any, prompt: str | FormatStr, kwargs: dict = None, with_context=True
) -> str:
    if not isinstance(prompt, (str, FormatStr)):
        raise TypeError("query_model accepts only str and FormatStr as prompt")
    name, conf, call = _prepare_model(model, model_kwargs=kwargs, call_async=False)
    if with_context:
        with Context(name, kind="query", inputs=dict(prompt=prompt, conf=conf)) as c:
            if isinstance(prompt, FormatStr):
                prompt = str(prompt)
            r = call(prompt)
            assert isinstance(r, str)
            c.set_result(r)
            return r
    else:
        return call(prompt)
