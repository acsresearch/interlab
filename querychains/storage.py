import gzip
import json
import os
from os import PathLike
from typing import List

from .context import Context
from .data import Data


class Storage:

    def write_context(self, context: Context):
        raise NotImplementedError

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

    def _file_path(self, parents, uuid: str) -> str:
        return os.path.join(self.directory, *parents, f"{uuid}.json.gz")

    def _dir_path(self, parents, uuid: str) -> str:
        return os.path.join(self.directory, *parents, f"{uuid}.ctx")

    def write_context(self, context: Context):
        if context.directory:
            self.write_context_dir([], context)
        else:
            self.write_context_file([], context.uuid, context.to_dict())

    def write_context_dir(self, parents: List[str], context: Context):
        path = self._dir_path(parents, context.uuid)
        tmp_path = path + "._tmp"
        os.mkdir()
        self.write("self", context.to_dict(with_children=False))

    def write_context_file(self, parents: List[str], context: Context, with_children=True):
        data = json.dumps(context.to_dict(with_children)).encode()
        path = self._file_path(parents, context.uuid)
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
            with gzip.open(self._file_path(uuid), "r") as f:
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
