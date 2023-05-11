from typing import Callable

from .context import Context
from .data import Data
from .utils import QueryFailure


def repeat_on_failure(fn: Callable, max_repeats=3, use_context=True) -> Data:
    for i in range(max_repeats):
        try:
            if use_context:
                name = f"{i + 1}/{max_repeats}"
                with Context(name=name, kind="repeat_on_failure") as c:
                    result = fn()
                    c.set_result(result)
                    return result
            else:
                return fn()
        except QueryFailure:
            continue
    raise QueryFailure(f"Subqueries failed on all {max_repeats} repetitions")
