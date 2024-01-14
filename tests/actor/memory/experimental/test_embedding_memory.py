from unittest.mock import MagicMock

from interlab.actor.memory.experimental.embedding_memory import SimpleEmbeddingMemory


def test_simple_embedding_memory():
    emb = MagicMock()
    m = SimpleEmbeddingMemory(emb)

    emb.embed_documents.return_value = [[1, 0, 0]]
    m.add_memory("A")
    emb.embed_documents.assert_called_with(["A"])
    m2 = m.copy()

    emb.embed_documents.return_value = [[0, 1, 0]]
    m.add_memory("B")
    emb.embed_documents.return_value = [[0, 0, 1]]
    m.add_memory("C")
    emb.embed_documents.return_value = [[1, 1, 0]]
    m.add_memory("AB")
    emb.embed_documents.return_value = [[0, 0, -1]]
    m.add_memory("c")
    assert m.count_memories() == 5
    assert m2.count_memories() == 1

    assert m.format_memories(separator="") == "ABCABc"
    assert m.format_memories(separator=" ", item_limit=3) == "C AB c"

    emb.embed_documents.return_value = [[0, 0, -1]]
    assert m.format_memories("X", separator=" ", item_limit=2) == "AB c"
    emb.embed_documents.return_value = [[0, 0, -1]]
    assert m.format_memories("X", separator=" ", item_limit=3) == "B AB c"
    emb.embed_documents.assert_called_with(["X"])

    emb.embed_documents.return_value = [[0.5, 0.6, 0]]
    assert m.format_memories("Y", separator=" ", item_limit=2) == "B AB"
    emb.embed_documents.return_value = [[-1, 0.1, 0.01]]
    assert m.format_memories("Z", separator=" ", token_limit=3) == "B C"
    emb.embed_documents.assert_called_with(["Z"])
    emb.embed_documents.return_value = [[-1, 0.1, 0.01]]
    assert m.format_memories("Z", separator=" ", token_limit=6) == "B C c"
