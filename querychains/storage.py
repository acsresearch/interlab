import gzip
import json
import os
from os import PathLike
from typing import List

from . import Data
from .context import Context


class Storage:
    def write_context(self, context: Context):
        self.write(context.uuid, context.to_dict())

    def write(self, uuid: str, data: Data):
        raise NotImplementedError

    def read(self, uuid: str) -> Data:
        raise NotImplementedError

    def list(self) -> List[str]:
        raise NotImplementedError


class FileStorage(Storage):
    def __init__(self, directory: PathLike | str):
        directory = os.path.abspath(directory)
        os.makedirs(directory, exist_ok=True)
        self.directory = directory

    def _path(self, uuid: str) -> str:
        return os.path.join(self.directory, f"{uuid}.json.gz")

    def write(self, uuid: str, data: Data):
        data = json.dumps(data).encode()
        path = self._path(uuid)
        tmp_path = path + "._tmp"
        try:
            with gzip.open(tmp_path, "w") as f:
                f.write(data)
            os.rename(tmp_path, path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def read(self, uuid: str) -> Data:
        try:
            with gzip.open(self._path(uuid), "r") as f:
                data = f.read()
        except FileNotFoundError:
            return None
        return json.loads(data)

    def list(self) -> List[str]:
        return [
            name[:-8]
            for name in os.listdir(self.directory)
            if name.endswith(".json.gz")
        ]

    def __repr__(self):
        return f"<FileStorage directory={repr(self.directory)}>"
