from unittest.mock import MagicMock, patch

from interlab.actor.memory import ListMemory

def test_list_memory():
    m = ListMemory()
    assert m.count_memories() == 0
    m.add_memory("A", time=2, data=42)
    m.add_memory("B", time=1)
    m.format_memories(formatter=lambda x: f"{x.memory}({x.time},{x.data})") == "A(2,42)\n\nB(1,None)"
    assert m.items[0].token_count == 1
    
    m2 = m.copy()
    m.add_memory("C", time=1)
    assert m.format_memories() == "A\n\nB\n\nC"
    assert m2.format_memories(separator=" ") == "A B"
    assert m2.count_memories() == 2

