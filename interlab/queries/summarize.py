import re
import warnings
from typing import Any

from ..context import with_context
from ..context.data.format_str import FormatStr
from ..lang_models import count_tokens, query_model


@with_context(name="Summarize with limit")
def summarize_with_limit(
    text: str, model: Any, token_limit: int = 300, length_request: str = None
):
    """Summarize text to within a token limit.

    Always summarizes even a shorter text (for style consistency).
    Iterates at most twice, then truncates the last summary by token count with " ..." added.

    Lenght request is e.g. "100 words" or "one paragraph" etc. By default, it is
    `f"{token_limit // } words"`.
    """
    if token_limit < 10:
        raise ValueError("Token limit must be at least 10.")
    if length_request is None:
        length_request = f"{token_limit // 2} words"
    # TODO: add a (large) token limit to the call below when query_model supports it
    summary = query_model(
        model,
        FormatStr("Summarize the following text in {length}:\n---\n{text}").format(
            length=length_request, text=text
        ),
    )

    # Second try - summarize the summary
    if count_tokens(summary, model) > token_limit:
        # TODO: add a (modest) token limit to the call below when query_model supports it
        summary = query_model(
            model,
            FormatStr(
                "Summarize the following text in much less than {length}:\n---\n{text}"
            ).format(length=length_request, text=summary),
        )

    # Fallback if the above fails
    # Note: count_tokens is cached so calling repeatedly is not a problem
    if count_tokens(summary, model) > token_limit:
        warnings.warn(
            f"Summarization failed to meet token limit again: got {count_tokens(summary, model)},"
            f" target {token_limit} tokens."
        )
        # Really trying to be robust in case the token count is HUGE
        while count_tokens(summary, model) > token_limit * 3:
            summary = summary[: len(summary) // 2]
        # Cut off parts separated by whitespace, punctuation, etc.
        while count_tokens(summary, model) > token_limit - 6:
            idx = re.search(
                r"(?s:.*)[\s.,;_=<>'\"&/!?()-]", summary, re.DOTALL | re.MULTILINE
            ).end()
            summary = summary[: idx - 1]
        summary = summary + " ..."
    return summary
