from dataclasses import dataclass
from typing import Union

import langchain
from serde.yaml import from_yaml

import copy
import interlab.actor.llm_actor
from interlab.actor import BaseActor


@dataclass
class Identity:
    name: str
    public: str
    private: str


@dataclass
class ModelConfig:
    name: str
    temp: float | None = None


@dataclass
class ActorConfig:
    type: str
    model: ModelConfig


@dataclass
class PersonaConfig:
    identity: Identity
    actor: ActorConfig


@dataclass
class ConfigFile:
    identities: dict[str, Identity]
    personas: dict[str, PersonaConfig] | None = None


class Persona(BaseActor):
    def __init__(self, config: PersonaConfig):
        super().__init__(config.identity.name)
        self.config = config
        self.actor = self._create_actor()

    def _observe(self, observation, time=None, data=None):
        return self.actor.observe(observation, time, data)

    def _query(self, prompt=None, **kwargs):
        return self.actor.query(prompt, **kwargs)

    def public_info(self, observer=None):
        return self.config.identity.public

    @staticmethod
    def _create_model(model: ModelConfig):
        return langchain.chat_models.ChatOpenAI(
            model_name=model.name, temperature=model.temp
        )

    def _create_actor(self):
        cfg = self.config
        if cfg.actor.type == "OneShotActor":
            return interlab.actor.llm_actor.OneShotLLMActor(
                cfg.identity.name,
                self._create_model(cfg.actor.model),
                self._system_prompt(),
            )

    def _system_prompt(self):
        identity = self.config.identity
        public = (
            f"Your public information are: {identity.public}\n"
            if identity.public
            else ""
        )
        private = (
            f"Your private information are: {identity.private}\n"
            if identity.private
            else ""
        )
        return f"You are {identity.name}\n{public}{private}"

    # def public_description(self, observer: Union[None, "Persona"] = None) -> str:
    #     return f"Public information about {self.config.identity.name}: {self.config.identity.public}\n"


class Factory:
    def __init__(self, personas):
        self.personas: dict[str, PersonaConfig] = personas

    @staticmethod
    def from_yaml(path):
        with open(path) as f:
            data = f.read()
        config = from_yaml(ConfigFile, data)
        return Factory(config.personas)

    def create_persona(
        self,
        key: str,
        name: str | None = None,
        public: str = "",
        private: str = "",
    ) -> Persona:
        person_cfg = self.personas.get(key)
        if person_cfg is None:
            raise Exception(f"Unknown persona '{key}'")
        person_cfg = copy.deepcopy(person_cfg)
        if name is not None:
            person_cfg.identity.name = name
        if public:
            person_cfg.identity.public += "\n" + public
        if private:
            person_cfg.identity.private += "\n" + private
        return Persona(person_cfg)
