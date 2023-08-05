import re

import pytest

from interlab.queries.summarize import summarize_with_limit


def test_summarize():
    class Model(str):
        def __call__(self, q):
            if "test1" in q:
                return "Short summary."
            if "test2" in q:
                return "Foo. Bar. Baz. Quux. " * 100
            if "Foo." in q:
                return "A#B-C#D-" * 10
            raise Exception(f"Unexpected query {q!r}.")

        def __repr__(self) -> str:
            return str(self)

    m = Model("gpt-3.5-turbo")

    assert summarize_with_limit("test1", m) == "Short summary."
    with pytest.warns(UserWarning, match=r"got 61, target 10 tokens"):
        assert re.fullmatch(
            r"A#B-? \.\.\.", summarize_with_limit("test2", m, token_limit=10)
        )
    with pytest.warns(UserWarning, match=r"got 61, target 20 tokens"):
        assert re.fullmatch(
            r"A#B-C#D-A#B-C#D(-A#)? \.\.\.",
            summarize_with_limit("test2", m, token_limit=20),
        )

    assert summarize_with_limit("test2", m, token_limit=100).endswith("C#D-A#B-C#D-")
    assert summarize_with_limit("test2", m, token_limit=1000).endswith(" Baz. Quux. ")
