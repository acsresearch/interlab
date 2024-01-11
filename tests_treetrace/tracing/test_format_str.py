import pytest

from treetrace.tracing.data.format_str import FormatStr


def test_fmtstring():
    S = "as{xyz}{{df{x#123:.3f}"
    f = FormatStr(S)
    assert str(f) == S
    assert str(f.format()) == str(f).replace("{{", "{")
    assert str(f.format(xyz="X")) == "asX{df{x#123:.3f}"
    assert str(f.format(xyz="X").format(x=0.3)) == "asX{df0.300"
    assert f.free_params() == {"xyz", "x"}
    f.into_html()

    S2 = "TST {aa} {x} {aa}"
    f2 = FormatStr(S2)
    assert f2.free_params() == {"aa", "x"}
    f2b = f2.format(aa=f.format(xyz="C"))
    assert str(f2b) == "TST asC{df{x#123:.3f} {x} asC{df{x#123:.3f}"

    # non-recursive and recursive subst
    assert str(f2b.format(x=42)) == "TST asC{df{x#123:.3f} 42 asC{df{x#123:.3f}"
    assert str(f2b.format(x=42, _recursive=True)) == "TST asC{df42.000 42 asC{df42.000"

    assert f2b.into_html().startswith("<span")

    x = FormatStr("a={a}") + "b={b}" + FormatStr("c={c}")
    assert isinstance(x, FormatStr)
    assert str(x) == "a={a}b={b}c={c}"
    assert str(x.format(a=1, b=2, c=3)) == "a=1b={b}c=3"

    y = FormatStr(" {x} ").join(["123", FormatStr("y={y}"), "456", FormatStr("x={x}Z")])
    assert isinstance(y, FormatStr)
    assert str(y) == "123 {x} y={y} {x} 456 {x} x={x}Z"
    assert str(y.format(x="X")) == "123 X y={y} X 456 X x=XZ"

    with pytest.raises(TypeError):
        x = " ".join([FormatStr("{a}"), "x"])

    with pytest.raises(TypeError):
        x = " " + FormatStr("{a}") + "x"

    bad_color = FormatStr("x={x#12z!r:3}")
    with pytest.raises(ValueError, match="color spec"):
        bad_color.into_html()
    with pytest.raises(ValueError, match="color spec"):
        bad_color.format(x="a").into_html()
