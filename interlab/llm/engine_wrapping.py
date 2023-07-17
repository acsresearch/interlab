from ..context import Context
from .engines import QueryEngine


def _prepare_engine(engine: any, engine_kwargs: dict = None, call_async: bool = False):
    import langchain
    import langchain.schema

    if call_async:
        raise NotImplementedError()
    if engine_kwargs is None:
        engine_kwargs = {}

    typename = engine.__class__.__name__
    conf = dict(_class=f"{engine.__class__.__module__}.{typename}")
    if isinstance(engine, langchain.llms.base.BaseLLM):
        conf.update(engine.dict())
        if "model_name" not in conf:
            conf["model_name"] = getattr(engine, "model", None)
        name = (
            f"Query langchain model {engine.__class__.__name__} ({conf['model_name']})"
        )
        call = lambda c: engine(c, **engine_kwargs)  # noqa: E731
    elif isinstance(engine, langchain.chat_models.base.BaseChatModel):
        conf.update(engine.dict())
        if "model_name" not in conf:
            conf["model_name"] = getattr(engine, "model", None)
        name = f"query langchain chat model {engine.__class__.__name__} ({conf['model_name']})"
        call = lambda c: engine(  # noqa: E731
            [langchain.schema.HumanMessage(content=c)], **engine_kwargs
        ).content
    elif isinstance(engine, QueryEngine):
        conf.update(model_name=engine.model, temperature=engine.temperature)
        name = (
            f"query interlab model {engine.__class__.__name__} ({conf['model_name']})"
        )
        call = lambda c: engine.query(c, **engine_kwargs)  # noqa: E731
    elif callable(engine):
        if hasattr(engine, "__name__"):
            name = f"query function {getattr(engine, '__module__', '<unknown>')}.{engine.__name__}"
        else:
            name = f"query engine {engine.__module__}.{engine.__class__.__name__}"
        getattr()

        call = lambda c: engine(c, **engine_kwargs)  # noqa: E731
    else:
        raise TypeError(f"Can't wrap engine of type {engine.__class__}")
    conf.update(**engine_kwargs)
    return name, conf, call


def query_engine(
    engine: any, prompt: str, kwargs: dict = None, with_context=True
) -> str:
    name, conf, call = _prepare_engine(engine, engine_kwargs=kwargs, call_async=False)
    if with_context:
        with Context(name, kind="query", inputs=dict(prompt=prompt, conf=conf)) as c:
            r = call(prompt)
            assert isinstance(r, str)
            c.set_result(r)
            return r
    else:
        return call(prompt)
