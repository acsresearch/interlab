from treetrace.utils.text import generate_uid, validate_uid


def test_validate_uid():
    assert not validate_uid("")
    assert validate_uid(generate_uid("abc"))
    assert validate_uid(generate_uid("*1*"))
    assert validate_uid(generate_uid("/abc/"))
    assert not validate_uid("/home/some/path")
    assert not validate_uid("*.txt")
