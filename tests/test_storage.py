import os

from querychains import Context
from querychains.storage import FileStorage


def test_file_storage(tmpdir):
    storage = FileStorage(os.path.join(tmpdir, "storage"))

    with Context("test1") as c1:
        with Context("test1-1"):
            pass

    storage.write_context(c1)

    ctx = storage.read(c1.uid)
    assert ctx == c1.to_dict()

    with Context("test2", storage=storage) as c2:
        pass

    ctx = storage.read(c2.uid)
    assert ctx == c2.to_dict()

    assert {c1.uid, c2.uid} == set(storage.list())


def test_file_storage_dirs(tmpdir):
    storage = FileStorage(os.path.join(tmpdir, "storage"))

    with Context("test1", directory=True) as c1:
        with Context("test1-1", directory=True):
            with Context("test-1-1-1"):
                pass
            with Context("test-1-1-2"):
                pass
        with Context("test1-2"):
            pass
        with Context("test1-3"):
            pass
        with Context("test1-4", directory=True):
            pass

    storage.write_context(c1)
    data = storage.read(c1.uid)
    assert data == c1.to_dict()
