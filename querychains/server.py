import asyncio

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from .context import Context


class ServerHandle:
    def __init__(self, port=0):
        self.port = port
        self.contexts = {}

    def start(self):
        loop = asyncio.get_event_loop()
        loop.create_task(_server_main(self))

    def add_context(self, context: Context):
        self.contexts[context.uuid] = context

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
        return [
            {"name": context.name, "uuid": context.uuid}
            for context in handle.contexts.values()
        ]

    @app.get("/contexts/uuid/{uuid}")
    async def list(uuid):
        ctx = handle.contexts.get(uuid)
        if ctx is None:
            raise HTTPException(status_code=404)
        return ctx.to_dict()

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


def start_server(port=0):
    handle = ServerHandle(port=port)
    handle.start()
    return handle
