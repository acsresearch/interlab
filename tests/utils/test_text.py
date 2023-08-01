from interlab.utils.text import ensure_newline, generate_uid, validate_uid


def test_ensure_new_lines():
    assert ensure_newline("", 1) == "\n"
    assert ensure_newline("aaaa", 1) == "aaaa\n"
    assert ensure_newline("\nbbb\n", 1) == "\nbbb\n"
    assert ensure_newline("cc\n\n", 1) == "cc\n\n"
    assert ensure_newline("\n", 1) == "\n"

    assert ensure_newline("", 3) == "\n\n\n"
    assert ensure_newline("aaaa", 3) == "aaaa\n\n\n"
    assert ensure_newline("\nbbb\n", 3) == "\nbbb\n\n\n"
    assert ensure_newline("\n", 3) == "\n\n\n"
    assert ensure_newline("zzz\n\n\n", 3) == "zzz\n\n\n"


def test_validate_uid():
    assert not validate_uid("")
    assert validate_uid(generate_uid("abc"))
    assert validate_uid(generate_uid("*1*"))
    assert validate_uid(generate_uid("/abc/"))
    assert not validate_uid("/home/some/path")
    assert not validate_uid("*.txt")
