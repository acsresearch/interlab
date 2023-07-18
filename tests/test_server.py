from interlab.context import Context


def test_server(storage):
    with Context("test1", storage=storage) as c1:
        with Context("test1-1"):
            pass

    with Context("test2", storage=storage) as c2:
        pass

    server = storage.start_server()
    try:
        raise Exception("TODO")
    finally:
        server.stop()
