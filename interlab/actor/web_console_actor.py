import json
from typing import Any

import dirtyjson

from treetrace import ConsoleServer

from ..queries import get_pydantic_model
from .base import BaseActor


class WebConsoleActor(BaseActor):
    def __init__(self, name: str, port: int = 0, **kwargs):
        super().__init__(name=name, **kwargs)
        self.server = ConsoleServer(f"Actor: {name}", port)

    def _observe(self, observation: str | Any, time: Any = None, data: Any = None):
        self.server.add_message(
            observation
        )  ## TODO(gavento): Somehow add time and data to the console?

    def _query(self, prompt: Any = None, expected_type=None):
        self.server.add_message(str(prompt))
        if expected_type is not None:
            T = get_pydantic_model(expected_type)
            self.server.add_message(
                "Format note: output is expected to be valid JSON of type\nSCHEMA\n"
                f"```json\n{json.dumps(T.schema())}\n```\nEND_OF_SCHEMA"
            )
        # TODO: Better support for JSON parsing etc
        r = self.server.receive()
        if expected_type is not None:
            r = T(**dirtyjson.loads(r))
            r = expected_type(r)
        return r

    @property
    def url(self):
        return self.server.url

    def display(self, width=1000, height=700):
        return self.server.display(width, height)
