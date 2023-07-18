from typing import Any

from interlab.actors import Actor, Event
from interlab.context.console_srv import ConsoleServer


class ConsoleActor(Actor):

    def __init__(self, name: str, port:int =0):
        super().__init__(name=name)
        self.server = ConsoleServer(f"Actor: {name}", port)

    def _observe(self, event: Event):
        self.server.add_message(event.data_as_string())

    def _act(self, prompt: Any = None):
        self.server.add_message(str(prompt))
        return self.server.receive()

    def display(self, width=1000, height=700):
        return self.server.display(height, width)