from unittest.mock import patch

from interlab.context import Context
from interlab.lang_models import OpenAiChatModel, Replay, query_model


@patch("interlab.lang_models.openai._make_openai_chat_query")
def test_replay_model(_make_openai_chat_query):
    model = OpenAiChatModel(api_key="xxx", api_org="xxx")
    with Context("root") as root:
        _make_openai_chat_query.return_value = "Answer 1"
        query_model(model, "How are you?")
        assert _make_openai_chat_query.call_count == 1
        _make_openai_chat_query.return_value = "Answer 2"
        query_model(model, "How are you?")
        assert _make_openai_chat_query.call_count == 2
        _make_openai_chat_query.return_value = "Answer 3"
        query_model(model, "What is your name?")
        assert _make_openai_chat_query.call_count == 3
        _make_openai_chat_query.return_value = "Answer 4"
        query_model(model, "How are you?")
        assert _make_openai_chat_query.call_count == 4

    replay = Replay(root)

    _make_openai_chat_query.return_value = "Answer 5"
    r = query_model(model, "How are you?", replay=replay)
    assert r == "Answer 1"

    model2 = OpenAiChatModel(api_key="xxx", api_org="xxx", temperature=0.0123)
    r = query_model(model2, "What is your name?", replay=replay)
    assert r == "Answer 5"

    r = query_model(model, "How are you?", replay=replay)
    assert r == "Answer 2"
    r = query_model(model, "How are you?", replay=replay)
    assert r == "Answer 4"
    r = query_model(model, "How are you?", replay=replay)
    assert r == "Answer 5"
    r = query_model(model, "What is your name?", replay=replay)
    assert r == "Answer 3"
