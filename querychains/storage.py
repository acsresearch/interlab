import gzip
import json
import os
import shutil
from os import PathLike
from typing import List, Sequence

from .context import Context
from .data import Data


class Storage:

    def __init__(self):
        self.ephemeral_contexts = {}

    def register_context(self, context: Context):
        self.ephemeral_contexts[context.uid] = context

    def write_context(self, context: Context):
        raise NotImplementedError

    def read(self, uid: str) -> Data:
        raise NotImplementedError

    def read_root(self, uid: str) -> Data:
        raise NotImplementedError

    def read_roots(self, uids: List[str]) -> List[Data]:
        raise NotImplementedError

    def list(self) -> List[str]:
        raise NotImplementedError

    def start_server(self, port=0):
        from .server import start_server
        return start_server(storage=self, port=port)


class FileStorage(Storage):
    def __init__(self, directory: PathLike | str):
        super().__init__()
        directory = os.path.abspath(directory)
        os.makedirs(directory, exist_ok=True)
        self.directory = directory

    def _file_path(self, directory, name) -> str:
        return os.path.join(directory, f"{name}.gz")

    def _dir_path(self, directory, name: str) -> str:
        return os.path.join(directory, f"{name}.ctx")

    def write_context(self, context: Context):
        self._write_context_into(self.directory, context)
        self.ephemeral_contexts.pop(context.uid, None)

    def _write_context_into(self, directory: str, context: Context):
        if context.directory:
            self._write_context_dir(directory, context)
        else:
            data = json.dumps(context.to_dict()).encode()
            data_root = json.dumps(context.to_dict(False)).encode()
            self._write_context_file(directory, context.uid + ".full", data)
            self._write_context_file(directory, context.uid + ".root", data_root)

    def _write_context_dir(self, directory: str, context: Context):
        path = self._dir_path(directory, context.uid)
        tmp_path = path + "._tmp"
        try:
            os.mkdir(tmp_path)
            data_root = json.dumps(context.to_dict(False)).encode()
            self._write_context_file(
                tmp_path, "_self", data_root
            )
            for child in context.children:
                self._write_context_into(tmp_path, child)
            os.rename(tmp_path, path)
        finally:
            if os.path.exists(tmp_path):
                shutil.rmtree(tmp_path)

    def _write_context_file(
        self, directory: str, name: str, data: Data
    ):
        path = self._file_path(directory, name)
        tmp_path = path + "._tmp"
        try:
            with gzip.open(tmp_path, "w") as f:
                f.write(data)
            os.rename(tmp_path, path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def read(self, uid: str) -> Data:
        context = self.ephemeral_contexts.get(uid)
        if context:
            return context.to_dict()

        return self._read_from(self.directory, uid)

    def read_root(self, uid) -> Data:
        context = self.ephemeral_contexts.get(uid)
        if context:
            return context.to_dict(with_children=False)

        dir_path = self._dir_path(self.directory, uid)
        if os.path.isdir(dir_path):
            path = self._file_path(dir_path, "_self")
        else:
            path = self._file_path(self.directory, uid + ".root")
        return self._read_file(path)

    def _read_from(self, directory: str, uid: str) -> Data:
        path = self._dir_path(directory, uid)
        if os.path.isdir(path):
            return self._read_dir(path)
        else:
            path = self._file_path(directory, uid + ".full")
            return self._read_file(path)

    def _read_file(self, path: str):
        with gzip.open(path, "r") as f:
            data = f.read()
        return json.loads(data)

    def _read_dir(self, path: str):
        self_path = self._file_path(path, "_self")
        self_data = self._read_file(self_path)
        children_uids = self_data.pop("children_uids", None)
        if children_uids is None:
            return self_data
        self_data["children"] = [self._read_from(path, uid) for uid in children_uids]
        return self_data

    def list(self) -> List[str]:
        file_suffix = ".root.gz"
        dir_suffix = ".ctx"

        lst = os.listdir(self.directory)
        return list(self.ephemeral_contexts.keys()) + [
            name[:-len(file_suffix)]
            for name in lst if name.endswith(file_suffix)
        ] + [
            name[:-len(dir_suffix)]
            for name in lst if name.endswith(dir_suffix)
        ]

    def read_roots(self, uids: Sequence[str]) -> List[Data]:
        return [self.read_root(uid) for uid in uids]

    def __repr__(self):
        return f"<FileStorage directory={repr(self.directory)}>"
