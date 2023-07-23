from interlab.llm import format_str


def test_fmtstring():
    S = "as{xyz}{{df{x:.3f}"
    f = format_str.FormatStr(S)
    assert str(f) == S
    assert str(f.format()) == str(f).replace("{{", "{")
    assert str(f.format(xyz="X")) == "asX{df{x:.3f}"
    assert str(f.format(xyz="X").format(x=0.3)) == "asX{df0.300"
    assert f.free_params() == {"xyz", "x"}

    S2 = "TST {aa} {x} {aa}"
    f2 = format_str.FormatStr(S2)
    assert f2.free_params() == {"aa", "x"}
    f2b = f2.format(aa=f.format(xyz="C"))
    assert str(f2b) == "TST asC{df{x:.3f} {x} asC{df{x:.3f}"

    # non-recursive and recursive subst
    assert str(f2b.format(x=42)) == "TST asC{df{x:.3f} 42 asC{df{x:.3f}"
    assert str(f2b.format(x=42, _recursive=True)) == "TST asC{df42.000 42 asC{df42.000"

    assert f2b.into_html().startswith("<span")
