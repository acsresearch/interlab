from interlab.actor.memory import ListMemory


def test_list_memory():
    m = ListMemory()
    assert m.count_memories() == 0
    m.add_memory("A", time=2, data=42)
    m.add_memory("B", time=1)
    m.format_memories(
        formatter=lambda x: f"{x.memory}({x.time},{x.data})"
    ) == "A(2,42)\n\nB(1,None)"
    assert m.items[0].token_count == 1

    m2 = m.copy()
    m.add_memory("C", time=1)
    assert m.format_memories() == "A\n\nB\n\nC"
    assert m2.format_memories(separator=" ") == "A B"
    assert m2.count_memories() == 2


def test_format_memories_helper():
    m = ListMemory()  # This test is not ListMemory specific
    m.add_memory("A", time=2, data=42)
    m.add_memory("B", time=4, data="Foo")
    m.add_memory("C", time=6)
    m.add_memory("D", time=7)
    m.add_memory("E", time=8)
    m.add_memory("F", time=10)
    assert m._format_memories_helper(m.items, separator="") == "ABCDEF"
    assert m._format_memories_helper(m.items[1:], separator="") == "BCDEF"
    assert (
        m._format_memories_helper(m.items[:3], formatter=lambda x: x.time) == "2\n\n4\n\n6"
    )
    assert m._format_memories_helper(m.items, item_limit=3) == "D\n\nE\n\nF"
    assert m._format_memories_helper(m.items, token_limit=4) == "E\n\nF"
    assert m._format_memories_helper(m.items, item_limit=4, token_limit=5) == "D\n\nE\n\nF"
    assert m._format_memories_helper(m.items, item_limit=4, token_limit=6, priorities=[6,2,5,4,3,1]) == "A\n\nC\n\nD"
    assert m._format_memories_helper(m.items, item_limit=4, token_limit=10, priorities=[6,2,5,4,3,1]) == "A\n\nC\n\nD\n\nE"
