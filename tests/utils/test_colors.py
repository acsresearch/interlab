from interlab.utils.html_color import HTMLColor


def test_colors():
    for s in ["#000000", "#00000000", "#ffffff", "#ffffffff", "#12345678", "#fedcba98"]:
        assert str(HTMLColor(s)) == s
    for s0, s1 in [("000", "#000000"), ("#fff1", "#ffffff11"), ("f926", "#ff992266")]:
        assert str(HTMLColor(s0)) == s1

    c = HTMLColor("#72e812")
    assert str(c.darker(1.0)) == "#000000"
    assert str(c.lighter(1.0)) == "#ffffff"
    assert str(c.darker()) == "#5bba0e"
    assert str(c.lighter()) == "#8ef03e"
    assert str(c.with_alpha(0.5)) == "#72e81280"

    # Testing hash functionality and stability
    # NOTE: may also be unstable due to float errors
    assert str(HTMLColor.random_color("Alice")) == "#2e49e1"
    assert str(HTMLColor.random_color(42)) == "#25c3aa"
