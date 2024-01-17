import copy

import pytest

import interlab.utils.copying as copying


def test_checked_deepcopy(monkeypatch):
    o1 = list(range(100))
    o2 = copying.checked_deepcopy(o1)
    assert o1 == o2
    assert id(o1) != id(o2)

    with pytest.warns(UserWarning, match="Deepcopy of"):
        o3 = copying.checked_deepcopy(o1, limit=10)
    assert o1 == o3
    assert id(o1) != id(o3)

    # Just to speed up the test
    monkeypatch.setattr(copying, "DEEPCOPY_WARN_LIMIT", 10000)

    p1 = list(range(10000))
    with pytest.warns(UserWarning, match="Deepcopy of"):
        p2 = copying.checked_deepcopy(p1)
    assert p1 == p2
    assert id(p1) != id(p2)

    p3 = copying.checked_deepcopy(p1, limit=None)
    assert p1 == p3
    assert id(p1) != id(p3)

    monkeypatch.setattr(copying, "DEEPCOPY_WARN_LIMIT", None)

    p4 = copying.checked_deepcopy(p1, limit=None)
    assert p1 == p4
    assert id(p1) != id(p4)


def test_immutable_wrapper():
    class A:
        def __init__(self, x):
            self.x = x

        def __call__(self, y):
            return self.x + y

        def foo(self):
            return list(reversed(self.x))

    a1 = A([1, 2, 3])
    a2 = copy.deepcopy(a1)
    assert id(a1) != id(a2)
    assert id(a1.x) != id(a2.x)
    assert a1.x == a2.x

    b1 = copying.ImmutableWrapper(a1)
    b2 = copy.deepcopy(b1)
    assert id(b1) == id(b2)
    assert id(b1._ImmutableWrapper_obj) == id(b2._ImmutableWrapper_obj)
    assert id(b1.x) == id(b2.x)
    assert b1.x == b2.x
    assert b2.x == [1, 2, 3]
    assert b1([42]) == [1, 2, 3, 42]
    assert b1.foo() == [3, 2, 1]

    b1.x.append(4)
    assert b2.x == [1, 2, 3, 4]

    assert isinstance(b1, copying.ImmutableWrapper)
    # assert isinstance(b, A) # TODO?
