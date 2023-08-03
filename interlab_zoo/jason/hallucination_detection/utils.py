from langchain import OpenAI
from langchain.chat_models import ChatOpenAI, ChatAnthropic
from omegaconf import DictConfig, OmegaConf
from pydantic.dataclasses import dataclass


@dataclass
class Result:
    completions: list[str]
    verdict: str


def get_engine(cfg: DictConfig):
    cfg = OmegaConf.to_container(cfg, resolve=True)
    model = cfg.pop("model")
    if model in ["gpt-3.5-turbo", "gpt-4"]:
        return ChatOpenAI(model_name=model, **cfg)
    if model in ["claude-1", "claude-2"]:
        return ChatAnthropic(model=model, **cfg)
    if model in ["text-curie-001", "text-davinci-003"]:
        return OpenAI(model_name=model, **cfg)
    raise ValueError(f"Unknown model name: {model}")
