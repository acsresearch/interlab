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
