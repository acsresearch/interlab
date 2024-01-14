from unittest.mock import patch

from interlab.actor.memory.experimental.summarizing_memory import SummarizingMemory


@patch("interlab.queries.summarize_with_limit")
def test_summarizing_memory(swl):
    m = SummarizingMemory("davinci", token_limit=90, separator=" ")
    assert m.count_memories() == 0
    ma = "A " * 30
    mb = "B " * 30
    m.add_memory(ma, time=1)
    assert m.items[0].token_count == 32
    m.add_memory(mb, time=2)
    assert m.items[1].token_count == 32
    m.format_memories() == ma + " " + mb
    assert m.count_memories() == 2
    assert m.total_tokens() == 64  # Separators are not counted
    m2 = m.copy()

    mc = "C " * 30
    swl.return_value = "ZZ"
    m.add_memory(mc, time=2)
    swl.assert_called_with(ma + " " + mb, model="davinci", token_limit=89)
    assert m.format_memories() == "ZZ " + mc
    assert m.count_memories() == 2
    assert m2.format_memories(separator="X") == ma + "X" + mb
