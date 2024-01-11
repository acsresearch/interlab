from treetrace import TracingNode
from treetrace import current_storage


def test_file_storage(storage):
    with TracingNode("test1") as c1:
        with TracingNode("test1-1"):
            pass

    storage.write_node(c1)

    ctx = storage.read(c1.uid)
    assert ctx == c1.to_dict()

    with TracingNode("test2", storage=storage) as c2:
        pass

    ctx = storage.read(c2.uid)
    assert ctx == c2.to_dict()

    assert {c1.uid, c2.uid} == set(storage.list())

    roots = storage.read_roots([c1.uid, c2.uid])
    assert roots[0] == c1.to_dict(with_children=False)
    assert roots[1] == c2.to_dict(with_children=False)

    assert storage.read_node(c2.uid).to_dict() == c2.to_dict()
    contexts = list(storage.read_all_nodes())
    assert len(contexts) == 2

    storage.remove_node(c2.uid)
    assert {c1.uid} == set(storage.list())


def test_file_storage_dirs(storage):
    with TracingNode("test1", directory=True) as c1:
        with TracingNode("test1-1", directory=True):
            with TracingNode("test-1-1-1"):
                pass
            with TracingNode("test-1-1-2"):
                pass
        with TracingNode("test1-2"):
            pass
        with TracingNode("test1-3"):
            pass
        with TracingNode("test1-4", directory=True):
            pass

    storage.write_node(c1)
    data = storage.read(c1.uid)
    assert data == c1.to_dict()

    assert storage.list() == [c1.uid]

    roots = storage.read_roots([c1.uid])
    assert roots[0] == c1.to_dict(with_children=False)

    storage.remove_node(c1.uid)
    assert storage.list() == []


def test_storage_with_block(storage):
    assert current_storage() is None
    with storage:
        assert current_storage() is storage
        with TracingNode("c") as c:
            with TracingNode("c2"):
                pass
    assert current_storage() is None
    assert storage.list() == [c.uid]

    with storage:
        assert current_storage() is storage
    assert current_storage() is None
