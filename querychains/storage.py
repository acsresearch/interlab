import gzip
import json
import os
import shutil
from os import PathLike
from typing import List

from .context import Context
from .data import Data


class Storage:

    def write_context(self, context: Context):
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

    def _file_path(self, directory, name) -> str:
        return os.path.join(directory, f"{name}.json.gz")

    def _dir_path(self, directory, name: str) -> str:
        return os.path.join(directory, f"{name}.ctx")

    def write_context(self, context: Context):
        self._write_context_into(self.directory, context)

    def _write_context_into(self, directory: str, context: Context):
        if context.directory:
            self._write_context_dir(directory, context)
        else:
            self._write_context_file(directory, context)

    def _write_context_dir(self, directory: str, context: Context):
        path = self._dir_path(directory, context.uuid)
        tmp_path = path + "._tmp"
        try:
            os.mkdir(tmp_path)
            self._write_context_file(tmp_path, context, with_children=False, name="_self")
            for child in context.children:
                self._write_context_into(tmp_path, child)
            os.rename(tmp_path, path)
        finally:
            if os.path.exists(tmp_path):
                shutil.rmtree(tmp_path)

    def _write_context_file(self, directory: str, context: Context, with_children=True, name=None):
        data = json.dumps(context.to_dict(with_children)).encode()
        path = self._file_path(directory, name or context.uuid)
        tmp_path = path + "._tmp"
        try:
            with gzip.open(tmp_path, "w") as f:
                f.write(data)
            os.rename(tmp_path, path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def read(self, uuid: str) -> Data:
        return self._read_from(self.directory, uuid)

    def _read_from(self, directory: str, uuid: str) -> Data:
        path = self._dir_path(directory, uuid)
        if os.path.isdir(path):
            return self._read_dir(path)
        else:
            path = self._file_path(directory, uuid)
            return self._read_file(path)

    def _read_file(self, path: str):
        with gzip.open(path, "r") as f:
            data = f.read()
        return json.loads(data)

    def _read_dir(self, path: str):
        self_path = self._file_path(path, "_self")
        self_data = self._read_file(self_path)
        children_uuids = self_data.pop("children_uuids", None)
        if children_uuids is None:
            return self_data
        self_data["children"] = [self._read_from(path, uuid) for uuid in children_uuids]
        return self_data

    def list(self) -> List[str]:
        return [
            name[:-8]
            for name in os.listdir(self.directory)
            if name.endswith(".json.gz")
        ]

    def __repr__(self):
        return f"<FileStorage directory={repr(self.directory)}>"
