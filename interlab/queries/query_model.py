from typing import Any

from treetrace import FormatStr, TracingNode

from .web_console import WebConsoleModel


def _prepare_model(model: Any, model_kwargs: dict = None, call_async: bool = False):
    import langchain_core as lc

    if call_async:
        raise NotImplementedError()
    if model_kwargs is None:
        model_kwargs = {}

    typename = model.__class__.__qualname__
    conf = {"class": f"{model.__class__.__module__}.{typename}"}
    if isinstance(model, lc.language_models.llms.BaseLLM):
        conf.update(model.dict())
        # For Anthropic (and maube other) langchain models:
        if "model_name" not in conf:
            conf["model_name"] = getattr(model, "model", None)
        name = f"Query langchain model {typename} ({conf['model_name']})"
        call = lambda c: model(c, **model_kwargs)  # noqa: E731
    elif isinstance(model, lc.language_models.chat_models.BaseChatModel):
        conf.update(model.dict())
        if "model_name" not in conf:
            conf["model_name"] = getattr(model, "model", None)
        name = f"query langchain chat model {typename} ({conf['model_name']})"
        call = lambda c: model(  # noqa: E731
            [lc.messages.human.HumanMessage(content=c)], **model_kwargs
        ).content
    elif isinstance(
        model, WebConsoleModel
    ):  # TODO: add some common base, or otherwise allow adding other model classes
        name, cfg = model.prepare_conf(**model_kwargs)
        conf.update(cfg)
        call = lambda c: model.query(c, conf)  # noqa: E731
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
    model: Any, prompt: str | FormatStr, kwargs: dict = None, with_trace=True
) -> str:
    if not isinstance(prompt, (str, FormatStr)):
        raise TypeError("query_model accepts only str and FormatStr as prompt")
    name, conf, call = _prepare_model(model, model_kwargs=kwargs, call_async=False)
    if with_trace:
        with TracingNode(
            name, kind="query", inputs=dict(prompt=prompt, conf=conf)
        ) as c:
            if isinstance(prompt, FormatStr):
                prompt = str(prompt)
            r = call(prompt)
            assert isinstance(r, str)
            c.set_result(r)
            return r
    else:
        return call(prompt)
