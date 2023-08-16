from typing import Any, Optional

from ..ui.console_server import ConsoleServer
from ..utils.text import group_newlines, remove_leading_spaces
from .base import LangModelBase


class WebConsoleModel(LangModelBase):
    def __init__(self, name: str, port: Optional[int] = 0):
        self.name = name
        self.server = ConsoleServer(name, port=port)

    def prepare_conf(self, **kwargs) -> (str, dict[str, Any]):
        return "query web console", {"name": self.name, "url": self.server.url}

    def _query(self, prompt: str, conf: dict[str, Any]) -> str:
        strip = conf.get("strip")
        if strip:
            prompt = remove_leading_spaces(group_newlines(prompt.strip()))
        self.server.clear()
        self.server.add_message(prompt)
        result = self.server.receive()
        if strip:
            result = group_newlines(result.strip())
        return result

    def display(self, width=900, height=500):
        return self.server.display(width, height)

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, url={self.server.url!r})"
