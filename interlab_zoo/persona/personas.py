from dataclasses import dataclass
from typing import Any
import yaml
from serde.yaml import from_yaml


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
    identity: str
    actor: ActorConfig


@dataclass
class ConfigFile:
    identities: dict[str, Identity]
    personas: dict[str, PersonaConfig] | None = None


class Persona:
    def __init__(self, identity: Identity, actor: BaseActor):
        pass


class Factory:
    def __init__(self, identities, personas):
        self.identities: str[str, Identity] = identities
        self.personas: dict[str, PersonaConfig] = personas

    @staticmethod
    def from_yaml(path):
        with open(path) as f:
            data = f.read()
        config = from_yaml(ConfigFile, data)
        return Factory(config.identities, config.personas)

    def get_identity(self, key: str) -> Identity:
        identity = self.personas.get(key)
        if identity is None:
            raise Exception(f"Identity '{key}' not found")
        return identity

    def create_persona(self, key: str) -> Persona:
        person_cfg = self.personas.get(key)
        if person_cfg is None:
            raise Exception(f"Persona '{key}' not found")
        identity = self.get_identity(person_cfg.identity)


# class Channel:

f = Factory.from_yaml("audience.yaml")
print(f)
