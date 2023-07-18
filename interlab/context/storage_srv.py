from typing import List
import os


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from .server import PATH_TO_STATIC_FILES, ServerHandle
from pydantic import BaseModel

from .storage import Storage
from ..utils import LOG


class RootsRequest(BaseModel):
    uids: List[str]


def _storage_app(storage) -> FastAPI:
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
        return storage.list()

    @app.post("/contexts/roots")
    async def get_roots(roots_request: RootsRequest):
        return storage.read_roots(roots_request.uids)

    @app.get("/contexts/uid/{uid}")
    async def get_uid(uid: str):
        data = storage.read(uid)
        if not data:
            raise HTTPException(status_code=404)
        return data
    return app


def start_storage_server(*, storage: Storage, port: int = 0) -> ServerHandle:
    handle = ServerHandle()
    handle.start(_storage_app(storage), port=port)
    LOG.info(f"Started context UI server: {handle}")
    return handle