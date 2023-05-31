import os

from querychains import Context
from querychains.storage import FileStorage


def test_file_storage(tmpdir):
    storage = FileStorage(os.path.join(tmpdir, "storage"))

    with Context("test1") as c1:
        with Context("test1-1"):
            pass

    storage.write_context(c1)

    ctx = storage.read(c1.uuid)
    assert ctx == c1.to_dict()

    with Context("test2", storage=storage) as c2:
        pass

    ctx = storage.read(c2.uuid)
    assert ctx == c2.to_dict()

    assert {c1.uuid, c2.uuid} == set(storage.list())

    assert storage.read("non-existent-id") is None
