import pytest

from interlab.queries.experimental.simple_tag_parsing import ParsingFailure, parse_tag


def test_parse_tag():
    assert (
        parse_tag("tg", "assa<f>ew <tg>1234\n533\r<<<<ggd>\n</tg> aa")
        == "1234\n533\r<<<<ggd>\n"
    )
    assert parse_tag("a", "ewew<a>edd</aa>") is None
    with pytest.raises(ParsingFailure, match="not found"):
        parse_tag("a", "ewew<a>edd</aa>", required=True)
    with pytest.raises(ParsingFailure, match="Multiple"):
        parse_tag("a", "ewew<a>edd</a> <a></a>")
