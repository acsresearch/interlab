from dataclasses import dataclass
from .engines import QueryEngine
from ..context import Context


@dataclass
class WrapperRunConfig:
    type: str
    full_type: str
    model_name: str | None = None
    model_kwargs: dict | None = None


def _prepare_engine(engine: any, engine_kwargs: dict = None, call_async: bool = False):
    import langchain
    import langchain.schema

    if call_async:
        raise NotImplementedError()
    if engine_kwargs is None:
        engine_kwargs = {}

    typename = engine.__class__.__name__
    conf = WrapperRunConfig(
        type=typename, full_type=f"{engine.__class__.__module__}.{typename}"
    )
    if isinstance(engine, langchain.llms.base.BaseLLM):
        conf.model_name = engine.model_name
        conf.model_kwargs = dict(engine.model_kwargs)
        name = f"Query langchain model {conf.type} ({conf.model_name})"
        call = lambda c: engine(c, **engine_kwargs)
    elif isinstance(engine, langchain.chat_models.base.BaseChatModel):
        conf.model_name = engine.model_name
        conf.model_kwargs = dict(engine.model_kwargs)
        name = f"query langchain chat model {conf.type} ({conf.model_name})"
        call = lambda c: engine(
            [langchain.schema.HumanMessage(content=c)], **engine_kwargs
        ).content
    elif isinstance(engine, QueryEngine):
        conf.model_name = engine.model
        conf.model_kwargs = dict(temperature=engine.temperature)
        name = f"query interlab model {conf.type} ({conf.model_name})"
        call = lambda c: engine.query(c, **engine_kwargs)
    elif callable(engine):
        conf.model_kwargs = {}
        name = "unknown engine"
        call = lambda c: engine(c, **engine_kwargs)
    else:
        raise TypeError(f"Can't wrap engine of type {engine.__class__}")
    conf.model_kwargs.update(**engine_kwargs)
    return name, conf, call


def query_engine(engine: any, prompt: str, kwargs: dict = None, with_context=True) -> str:
    name, conf, call = _prepare_engine(engine, engine_kwargs=kwargs, call_async=False)
    if with_context:
        with Context(name, kind="query", inputs=dict(prompt=prompt, conf=conf)) as c:
            r = call(prompt)
            assert isinstance(r, str)
            c.set_result(r)
            return r
    else:
        return call(prompt)
