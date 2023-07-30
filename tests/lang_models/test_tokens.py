import langchain.chat_models
import pytest

import interlab.lang_models
from interlab.lang_models.count_tokens import count_tokens

TEXT = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed ultrices lacus sed leo ornare, "
    "sed iaculis mi pharetra. Pellentesque non nisi vitae diam sodales commodo."
)


def test_count_tokens():
    assert count_tokens(TEXT, "gpt2") == 56
    assert count_tokens(TEXT, "gpt-4") == 40
    assert count_tokens(TEXT, "claude-2") == 57
    with pytest.raises(ValueError):
        count_tokens(TEXT, "foobar")
    assert count_tokens(TEXT, interlab.lang_models.AnthropicModel()) == 57
    assert count_tokens(TEXT, interlab.lang_models.OpenAiChatModel("gpt-4")) == 40
    assert count_tokens(TEXT, langchain.chat_models.ChatOpenAI(model="gpt-4")) == 40
    assert count_tokens(TEXT, langchain.chat_models.ChatOpenAI()) == 40
    assert count_tokens(TEXT, langchain.chat_models.ChatAnthropic()) == 57
    assert count_tokens(TEXT, langchain.OpenAI()) == 56
