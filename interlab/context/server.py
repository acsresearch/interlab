import asyncio
import importlib.resources as resources
from threading import Condition

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import browser

with resources.path(browser, ".") as static_path:
    PATH_TO_STATIC_FILES = static_path


class ServerHandle:
    def __init__(self):
        self.port = None
        self.task = None
        self.server = None
        self.loop = None

    def stop(self):
        if self.server:
            self.server.should_exit = True

    def start(self, app: FastAPI, port=0):
        from IPython.lib import backgroundjobs as bg

        app.mount("/", StaticFiles(directory=PATH_TO_STATIC_FILES), name="static")

        config = uvicorn.Config(app, port=port, log_level="error")
        server = uvicorn.Server(config)

        def _helper():
            asyncio.run(_server_main(self, server, cv))

        cv = Condition()
        jobs = bg.BackgroundJobManager()
        jobs.new(_helper)
        with cv:  # Wait for port assignment
            cv.wait()
        self.server = server

    def serve_forever(self):
        loop = asyncio.get_event_loop()
        loop.run_forever()

    @property
    def url(self):
        return f"http://localhost:{self.port}"

    def __repr__(self):
        return f"<ServerHandle {self.url}>"


async def _server_main(handle: ServerHandle, server, cv: Condition):
    async def _wait_for_port(server):
        while not server.started:
            await asyncio.sleep(0.1)
        if server.servers:
            s = server.servers[0]
            if s.sockets:
                _, port = s.sockets[0].getsockname()
                handle.port = port
        with cv:
            cv.notify_all()

    handle.loop = asyncio.get_running_loop()
    asyncio.create_task(_wait_for_port(server))
    await server.serve()
