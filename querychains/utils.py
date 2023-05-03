import logging
from typing import Union

from addict import Dict

LOG = logging.getLogger("querychains")


class QueryFailure(Exception):
    pass


# Initially lets just have arbitrary dict
Data = Dict

IntoData = Union[str, Data, dict]


def into_data(d: IntoData):
    if isinstance(d, str):
        d = dict(text=d)
    assert isinstance(d, dict)
    return Dict(d)


def shorten_str(s: str | None, max_len=32) -> str:
    if s is None:
        return "None"
    r = repr(s)
    if len(r) <= max_len:
        return r
    return r[: max_len - 5] + "[...]"
