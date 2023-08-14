import asyncio
import logging
import os
import threading
from typing import List

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.websockets import WebSocketDisconnect

from ..utils.display import display_iframe
from .server_handle import PATH_TO_STATIC_FILES, ServerHandle

_LOG = logging.getLogger(__name__)


class ConsoleState:
    def __init__(self, name: str):
        self.name = name
        self.sockets: List[WebSocket] = []
        self.messages = []
        self.input_futures = []

    async def add_socket(self, socket: WebSocket):
        self.sockets.append(socket)
        await socket.send_json({"type": "input", "value": bool(self.input_futures)})
        if self.messages:
            await socket.send_json(self.messages)

    def remove_socket(self, socket: WebSocket):
        self.sockets.remove(socket)

    async def add_message(self, text: str, echo: bool = False):
        message = {
            "type": "message",
            "id": len(self.messages),
            "text": text,
            "echo": bool(echo),
        }
        self.messages.append(message)
        await self.broadcast(message)

    async def wait_for_input(self):
        f = asyncio.Future()
        self.input_futures.append(f)
        if len(self.input_futures) == 1:
            await self.send_input_state(True)
        return await f

    async def on_input(self, text):
        if not self.input_futures:
            return
        future = self.input_futures.pop()
        await self.add_message(text, echo=True)
        if not self.input_futures:
            await self.send_input_state(False)
        future.set_result(text)

    async def send_input_state(self, value: bool):
        await self.broadcast(
            {
                "type": "input",
                "value": value,
            }
        )

    async def broadcast(self, data):
        if not self.sockets:
            return
        results = [asyncio.create_task(s.send_json(data)) for s in self.sockets]
        await asyncio.wait(results)

    async def clear(self):
        self.messages = []
        for f in self.input_futures:
            f.set_exception(Exception("Receive cancelled"))
        await self.broadcast({"type": "init", "name": self.name})


def _console_app(state: ConsoleState) -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/console")
    async def root():
        return FileResponse(os.path.join(PATH_TO_STATIC_FILES, "index.html"))

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        await websocket.send_json({"type": "init", "name": state.name})
        await state.add_socket(websocket)
        try:
            try:
                while True:
                    text = await websocket.receive_text()
                    await state.on_input(text)
            except WebSocketDisconnect:
                pass
        finally:
            state.remove_socket(websocket)

    return app


class ConsoleServer:
    def __init__(self, name: str, port=None):
        state = ConsoleState(name)
        handle = ServerHandle()
        handle.start(_console_app(state), port=port)
        self.handle = handle
        self.state = state
        _LOG.info(f"Created console UI at {self.url}")

    @property
    def url(self):
        return self.handle.url + "/console"

    def stop(self):
        self.handle.stop()

    def add_message(self, message):
        async def _helper():
            await self.state.add_message(message)

        self.handle.loop.call_soon_threadsafe(asyncio.create_task, _helper())

    def clear(self):
        event = threading.Event()

        async def _helper():
            await self.state.clear()
            event.set()

        self.handle.loop.call_soon_threadsafe(asyncio.create_task, _helper())
        event.wait()

    def receive(self):
        event = threading.Event()

        async def _helper():
            event.my_result = await self.state.wait_for_input()
            event.set()

        self.handle.loop.call_soon_threadsafe(asyncio.create_task, _helper())
        event.wait()
        return event.my_result  # noqa

    def display(self, width="95%", height=700):
        display_iframe(self.url, self.handle.port, width, height)
