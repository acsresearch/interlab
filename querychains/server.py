import asyncio
import os
from typing import Optional, List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.responses import FileResponse

from .context import Context
from .storage import Storage

PATH_TO_STATIC_FILES = "browser/build/"


class ServerHandle:
    def __init__(self, storage: Storage, port: int = 0):
        self.port = port
        self.storage = storage
        self.task = None

    def start(self):
        from IPython.lib import backgroundjobs as bg

        def _helper():
            asyncio.run(_server_main(self))
        jobs = bg.BackgroundJobManager()
        jobs.new(_helper)

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
        return FileResponse(os.path.join(PATH_TO_STATIC_FILES, "index.html"))

    @app.get("/contexts/list")
    async def list_of_contexts():
        return handle.storage.list()

    class RootsRequest(BaseModel):
        uids: List[str]

    @app.post("/contexts/roots")
    async def get_roots(roots_request: RootsRequest):
        return handle.storage.read_roots(roots_request.uids)

    @app.get("/contexts/uid/{uid}")
    async def get_uid(uid: str):
        data = handle.storage.read(uid)
        if not data:
            raise HTTPException(status_code=404)
        return data

    app.mount("/", StaticFiles(directory=PATH_TO_STATIC_FILES), name="static")

    config = uvicorn.Config(app, port=handle.port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


def start_server(*, storage: Optional[Storage] = None, port: int = 0):
    handle = ServerHandle(storage=storage, port=port)
    handle.start()
    return handle
