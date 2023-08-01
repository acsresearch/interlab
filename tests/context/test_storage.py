from interlab.context import Context


def test_file_storage(storage):
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

    roots = storage.read_roots([c1.uid, c2.uid])
    assert roots[0] == c1.to_dict(with_children=False)
    assert roots[1] == c2.to_dict(with_children=False)

    assert storage.read_context(c2.uid).to_dict() == c2.to_dict()
    contexts = list(storage.read_all_contexts())
    assert len(contexts) == 2

    storage.remove_context(c2.uid)
    assert {c1.uid} == set(storage.list())


def test_file_storage_dirs(storage):
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

    assert storage.list() == [c1.uid]

    roots = storage.read_roots([c1.uid])
    assert roots[0] == c1.to_dict(with_children=False)

    storage.remove_context(c1.uid)
    assert storage.list() == []
