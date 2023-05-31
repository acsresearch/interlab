import asyncio
from typing import Annotated, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from .context import Context
from .storage import Storage


class ServerHandle:
    def __init__(self, storage: Optional[Storage] = None, port=0):
        self.port = port
        self.storage = storage
        self.contexts = {}
        self.task = None

    def start(self):
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(_server_main(self))

    def add_context(self, context: Context):
        self.contexts[context.uuid] = context

    def serve_forever(self):
        loop = asyncio.get_event_loop()
        loop.run_forever()

    def __repr__(self):
        # TODO: Return assigned port
        return "<ServerHandle>"


async def _server_main(handle: ServerHandle):
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return FileResponse("browser/browser/build/index.html")

    @app.get("/contexts/list")
    async def list_of_contexts():
        return (
            [uuid for uuid in handle.contexts.keys()] + handle.storage.list()
            if handle.storage
            else []
        )

    @app.get("/contexts/uuid/{uuid}")
    async def get_uuid(uuid: str):
        # Check format of uuid
        ctx = handle.contexts.get(uuid)
        if ctx is not None:
            return ctx.to_dict()

        if handle.storage:
            data = handle.storage.read(uuid)
            if data:
                return data

        raise HTTPException(status_code=404)

    app.mount("/", StaticFiles(directory="browser/browser/build/"), name="static")

    config = uvicorn.Config(app, port=handle.port, log_level="info")
    server = uvicorn.Server(config)
    asyncio.create_task(server.serve())

    while not server.started:
        await asyncio.sleep(0.1)

    for server in server.servers:
        for socket in server.sockets:
            addr, port = socket.getsockname()
            return f"{addr}:{port}"


def start_server(*, storage: Optional[Storage] = None, port: int = 0):
    handle = ServerHandle(storage=storage, port=port)
    handle.start()
    return handle
