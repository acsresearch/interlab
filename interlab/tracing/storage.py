import abc
import contextvars
import gzip
import json
import os
import shutil
import threading
from os import PathLike
from typing import Callable, Iterator, List, Optional, Sequence

from ..utils.display import display_iframe
from ..utils.text import validate_uid
from .tracingnode import TracingNode
from .serialization import Data

_STORAGE_STACK = contextvars.ContextVar("_STORAGE_STACK", default=())


class StorageBase(abc.ABC):
    def __init__(self):
        self._lock = threading.Lock()
        self._ephemeral_nodes = {}
        self._server = None
        self._token = None

    def register_node(self, node: TracingNode):
        """Register running tracing node (without writing into the persistent storage)"""
        with self._lock:
            self._ephemeral_nodes[node.uid] = node

    def get_ephemeral_node(self, uid: str) -> Optional[TracingNode]:
        """Get running tracing node (not from persistent storage)"""
        with self._lock:
            return self._ephemeral_nodes.get(uid)

    @abc.abstractmethod
    def write_node(self, node: TracingNode):
        """Write tracing node into persistent storage"""
        raise NotImplementedError

    @abc.abstractmethod
    def read(self, uid: str) -> Data:
        """Read unserialized tracing from the storage"""
        raise NotImplementedError

    @abc.abstractmethod
    def read_root(self, uid: str) -> Data:
        """Read tracing without children"""
        raise NotImplementedError

    @abc.abstractmethod
    def remove_node(self, uid: str):
        """Remove tracing from storage"""
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> List[str]:
        """List all tracing uids in storage"""
        raise NotImplementedError

    def read_roots(self, uids: Sequence[str]) -> List[Data]:
        """Read given root nodes without children"""
        return [self.read_root(uid) for uid in uids]

    def read_node(self, uid: str) -> TracingNode:
        """Read and serialize tracing node from storage"""
        return TracingNode.deserialize(self.read(uid))

    def read_all_nodes(self) -> Iterator[TracingNode]:
        """Read all nodes from storage"""
        for uid in self.list():
            yield self.read_node(uid)

    def live_display(self, width="95%", height=700):
        """Show tracing in Jupyter notebook"""
        if self._server is None:
            self.start_server()
        display_iframe(self._server.url, self._server.port, width, height)

    @property
    def server(self):
        if self._server is None:
            raise Exception("Server not stared. Use method 'start_server' on storage")
        return self._server

    def start_server(self, port=0):
        if self._server is not None:
            raise Exception("Server already started")
        from ..ui.storage_server import start_storage_server

        self._server = start_storage_server(storage=self, port=port)
        return self._server

    def find_nodes(self, predicate: Callable) -> Iterator[TracingNode]:
        for node in self.read_all_nodes():
            yield from node.find_nodes(predicate)

    def __enter__(self):
        if self._token:
            raise Exception("Storage is already active")
        old = _STORAGE_STACK.get()
        self._token = _STORAGE_STACK.set(old + (self,))
        return self

    def __exit__(self, _exc_type, exc_val, _exc_tb):
        _STORAGE_STACK.reset(self._token)
        self._token = False


def current_storage() -> Optional[StorageBase]:
    stack = _STORAGE_STACK.get()
    if not stack:
        return None
    return stack[-1]


class FileStorage(StorageBase):
    def __init__(self, directory: PathLike | str):
        super().__init__()
        directory = os.path.abspath(directory)
        os.makedirs(directory, exist_ok=True)
        self.directory = directory

    def _file_path(self, directory, name) -> str:
        return os.path.join(directory, f"{name}.gz")

    def _dir_path(self, directory, name: str) -> str:
        return os.path.join(directory, f"{name}.ctx")

    def write_node(self, node: TracingNode):
        if not validate_uid(node.uid):
            raise Exception("Invalid uid")
        self._write_node_into(self.directory, node, True)
        with self._lock:
            self._ephemeral_nodes.pop(node.uid, None)

    def _write_node_into(self, directory: str, node: TracingNode, root_node: bool):
        if not validate_uid(node.uid):
            raise Exception("Invalid uid")
        if node.directory:
            self._write_node_dir(directory, node, root_node)
        else:
            data = json.dumps(node.to_dict(root=root_node)).encode()
            data_root = json.dumps(node.to_dict(False, root=root_node)).encode()
            # Write full first, so when root exists, then full is definitely there
            self._write_node_file(directory, node.uid + ".full", data)
            self._write_node_file(directory, node.uid + ".root", data_root)

    def _write_node_dir(self, directory: str, node: TracingNode, node_content: bool):
        path = self._dir_path(directory, node.uid)
        tmp_path = path + "._tmp"
        try:
            os.mkdir(tmp_path)
            data_root = json.dumps(node.to_dict(False, root=node_content)).encode()
            self._write_node_file(tmp_path, "_self", data_root)
            for child in node.children:
                self._write_node_into(tmp_path, child, False)
            os.rename(tmp_path, path)
        finally:
            if os.path.exists(tmp_path):
                shutil.rmtree(tmp_path)

    def _write_node_file(self, directory: str, name: str, data: Data):
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
        if not validate_uid(uid):
            raise Exception("Invalid uid")
        node = self.get_ephemeral_node(uid)
        if node:
            return node.to_dict()
        return self._read_from(self.directory, uid)

    def read_root(self, uid) -> Data:
        if not validate_uid(uid):
            raise Exception("Invalid uid")
        node = self.get_ephemeral_node(uid)
        if node:
            return node.to_dict(with_children=False)

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

        with self._lock:
            ephemeral = list(self._ephemeral_nodes.keys())

        lst = os.listdir(self.directory)
        return (
            ephemeral
            + [name[: -len(file_suffix)] for name in lst if name.endswith(file_suffix)]
            + [name[: -len(dir_suffix)] for name in lst if name.endswith(dir_suffix)]
        )

    def remove_node(self, uid: str):
        if not validate_uid(uid):
            raise Exception("Invalid uid")
        # First try to remove .root, so it immediately disappear from listing
        path = self._file_path(self.directory, uid + ".root")
        if os.path.isfile(path):
            os.unlink(path)
            path = self._file_path(self.directory, uid + ".full")
            os.unlink(path)
        else:
            path = self._dir_path(self.directory, uid)
            if os.path.isdir(path):
                shutil.rmtree(path)
        with self._lock:
            self._ephemeral_nodes.pop(uid, None)

    def __repr__(self):
        return f"<FileStorage directory={repr(self.directory)}>"
