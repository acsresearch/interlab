from typing import Type, Any
from dataclasses import dataclass


@dataclass
class Affordance:
    name: str
    description: str | None = None
    args_type: Type | None = None


@dataclass
class Action:
    affordance: Affordance
    args: Any
