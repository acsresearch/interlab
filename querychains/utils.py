import logging

LOG = logging.getLogger("querychains")


class QueryFailure(Exception):
    pass


def shorten_str(s: str | None, max_len=32) -> str:
    if s is None:
        return "None"
    r = repr(s)
    if len(r) <= max_len:
        return r
    return r[: max_len - 5] + "[...]"
