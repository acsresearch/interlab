import langchain_openai

# Disable because of version conflict
# import langchain_anthropic
import pytest

from interlab.queries.count_tokens import count_tokens

TEXT = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed ultrices lacus sed leo ornare, "
    "sed iaculis mi pharetra. Pellentesque non nisi vitae diam sodales commodo."
)


def test_count_tokens():
    count_tokens.cache_clear()  # To have clean hit counting below

    assert count_tokens(TEXT, "gpt2") == 56
    assert count_tokens(TEXT, "text-curie-001") == 56
    assert count_tokens(TEXT, "claude-2") == 57
    with pytest.raises(ValueError):
        count_tokens(TEXT, "foobar")
    assert (
        count_tokens(
            TEXT,
            langchain_openai.ChatOpenAI(model="gpt-4", openai_api_key="Foo"),
        )
        == 40
    )
    assert (
        count_tokens(
            TEXT,
            langchain_openai.ChatOpenAI(openai_api_key="Foo"),
        )
        == 40
    )
    # assert (
    #     count_tokens(
    #         TEXT, langchain_community.chat_models.ChatAnthropic(anthropic_api_key="Foo")
    #     )
    #     == 57
    # )
    assert (
        count_tokens(
            TEXT, langchain_openai.OpenAI(model="babbage", openai_api_key="Foo")
        )
        == 56
    )
    assert count_tokens.cache_info().hits == 0
    assert (
        count_tokens(
            TEXT, langchain_openai.OpenAI(model="babbage", openai_api_key="Foo")
        )
        == 56
    )
    assert count_tokens.cache_info().hits == 1
