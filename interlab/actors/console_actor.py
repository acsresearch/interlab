import json
from dataclasses import dataclass
from typing import Any

from interlab.actors import Actor, Event
from interlab.context.console_srv import ConsoleServer

from ..llm.json_parsing import into_pydantic_model


class ConsoleActor(Actor):
    def __init__(self, name: str, port: int = 0):
        super().__init__(name=name)
        self.server = ConsoleServer(f"Actor: {name}", port)

    def _observe(self, event: Event):
        self.server.add_message(event.data_as_string())

    def _act(self, prompt: Any = None, expected_type=None):
        self.server.add_message(str(prompt))
        if expected_type is not None:
            T = into_pydantic_model(expected_type)
            self.server.add_message(
                f"Format note: output is expected to be valid JSON of type {T.schema()}"
            )
        # TODO: Better support for JSON parsing etc
        r = self.server.receive()
        if expected_type is not None:
            r = T(**json.loads(r))
        return r

    def display(self, width=1000, height=700):
        return self.server.display(width, height)
