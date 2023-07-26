import asyncio
import json

import pytest
import websockets

from interlab.ui.console_srv import ConsoleServer


@pytest.mark.asyncio
async def test_console_server():
    server = ConsoleServer("My console")
    server.add_message("First message")
    url = (server.handle.url + "/ws").replace("http", "ws")

    try:
        async with websockets.connect(url) as websocket:
            msg = await websocket.recv()
            assert json.loads(msg) == {"type": "init", "name": "My console"}
            msg = await websocket.recv()
            assert json.loads(msg) == {"type": "input", "value": False}
            msg = await websocket.recv()
            assert json.loads(msg) == [
                {"id": 0, "text": "First message", "type": "message"}
            ]
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(websocket.recv(), timeout=0.3)
            server.add_message("Second message")
            msg = await websocket.recv()
            assert json.loads(msg) == {
                "id": 1,
                "text": "Second message",
                "type": "message",
            }
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(websocket.recv(), timeout=0.3)
    finally:
        server.stop()
