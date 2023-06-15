from enum import Enum
from typing import Any, List, Optional, Dict
from dataclasses import dataclass

from .context import with_context, add_event, Context
from .utils import short_repr


@dataclass
class EventObservation:
    data: Any


@dataclass
class EventAction:
    prompt: Any
    action: Any


class Actor:

    def __init__(self, name: Optional[str] = None, ctx_meta: Optional[Dict]=None):
        self.name = name or self.__class__.__name__
        self.events: List[EventAction | EventObservation] = []
        self.ctx_meta = ctx_meta


    def observations(self):
        return [event.data for event in self.events if isinstance(event, EventObservation)]

    def actions(self):
        return [event.action for event in self.events if isinstance(event, EventAction)]

    async def act(self, prompt: Any = None):
        with Context(f"Action of {self.name}: {short_repr(prompt)}", kind="action", meta=self.ctx_meta, inputs={
            "prompt": prompt,
        }) as c:
            action = await self.compute_action(prompt)
            self.events.append(EventAction(prompt, action))
            c.set_result(action)
        return action

    async def compute_action(self, prompt: Any):
        raise NotImplementedError

    def observe(self, data: Any):
        self.events.append(EventObservation(data))
        with Context(f"Observation of {self.name}: {short_repr(data)}", kind="observation", meta=self.ctx_meta, inputs={"observation": data}):
            self.process_observe(data)

    def process_observe(self, data: Any):
        pass

    def __repr__(self):
        return f"<Actor {self.name}>"

# TODO:

class ActorProcess(Actor):

    async def process_act(self, prompt: Any):
        pass

    async def main(self):
        raise NotImplementedError