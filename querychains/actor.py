from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .context import Context
from .utils import short_repr


@dataclass
class EventObservation:
    data: Any


@dataclass
class EventAction:
    prompt: Any
    action: Any


class Actor:
    def __init__(self, name: Optional[str] = None, ctx_meta: Optional[Dict] = None):
        self.name = name or self.__class__.__name__
        self.events: List[EventAction | EventObservation] = []
        self.ctx_meta = ctx_meta

    def observations(self):
        return [
            event.data for event in self.events if isinstance(event, EventObservation)
        ]

    def actions(self):
        return [event.action for event in self.events if isinstance(event, EventAction)]

    def act(self, prompt: Any = None):
        if prompt:
            name = f"Action of {self.name}: {short_repr(prompt)}"
            inputs = {
                "prompt": prompt,
            }
        else:
            name = f"Action of {self.name}"
            inputs = None
        with Context(name, kind="action", meta=self.ctx_meta, inputs=inputs) as c:
            action = self.get_action(prompt)
            self.events.append(EventAction(prompt, action))
            c.set_result(action)
        return action

    def get_action(self, prompt: Any):
        raise NotImplementedError

    def observe(self, data: Any):
        self.events.append(EventObservation(data))
        with Context(
            f"Observation of {self.name}: {short_repr(data)}",
            kind="observation",
            meta=self.ctx_meta,
            inputs={"observation": data},
        ):
            self.process_observation(data)

    def process_observation(self, data: Any):
        pass

    def __repr__(self):
        return f"<Actor {self.name}>"


# TODO:


class ActorProcess(Actor):
    async def process_act(self, prompt: Any):
        pass

    async def main(self):
        raise NotImplementedError
