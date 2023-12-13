import requests

from interlab.tracing import TracingNode


def test_server(storage):
    with TracingNode("test1", storage=storage) as c1:
        with TracingNode("test1-1"):
            pass

    with TracingNode("test2", storage=storage) as c2:
        pass

    server = storage.start_server()
    url = server.url
    try:
        r = requests.get(url + "/nodes/list")
        assert r.status_code == 200
        assert set(r.json()) == {c1.uid, c2.uid}

        for c in (c1, c2):
            r = requests.get(url + f"/nodes/uid/{c.uid}")
            assert r.status_code == 200
            assert r.json() == c.to_dict()

        r = requests.post(url + "/nodes/roots", json={"uids": [c1.uid]})
        assert r.status_code == 200
        assert r.json() == [c1.to_dict(with_children=False)]

        r = requests.delete(url + f"/nodes/uid/{c1.uid}")
        assert r.status_code == 200

        r = requests.get(url + "/nodes/list")
        assert r.status_code == 200
        assert set(r.json()) == {c2.uid}

    finally:
        server.stop()
