import logging
import os
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import FileResponse

from ..context.storage import StorageBase
from .server_handle import PATH_TO_STATIC_FILES, ServerHandle

_LOG = logging.getLogger(__name__)


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

    @app.delete("/contexts/uid/{uid}")
    async def delete_uid(uid: str):
        storage.remove_context(uid)

    return app


def start_storage_server(*, storage: StorageBase, port: int = 0) -> ServerHandle:
    handle = ServerHandle()
    handle.start(_storage_app(storage), port=port)
    _LOG.info(f"Started context UI server: {handle}")
    return handle
