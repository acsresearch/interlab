from typing import Awaitable, Callable

from ...context import Context
from ...queries import QueryFailure


def repeat_on_failure(
    fn: Callable, max_repeats=3, use_context=True, throw_if_fail=True, fail_value=None
):
    for i in range(max_repeats):
        try:
            if use_context:
                name = f"{fn.__name__}: {i + 1}/{max_repeats}"
                with Context(name=name, kind="repeat_on_failure") as c:
                    result = fn()
                    c.set_result(result)
                    return result
            else:
                return fn()
        except QueryFailure:
            continue
    if throw_if_fail:
        raise QueryFailure(f"Subqueries failed on all {max_repeats} repetitions")
    else:
        return fail_value


async def async_repeat_on_failure(
    fn: Awaitable, max_repeats=3, use_context=True, throw_if_fail=True, fail_value=None
):
    for i in range(max_repeats):
        try:
            if use_context:
                name = f"{i + 1}/{max_repeats}"
                with Context(name=name, kind="async_repeat_on_failure") as c:
                    result = await fn()
                    c.set_result(result)
                    return result
            else:
                return await fn()
        except QueryFailure:
            continue
    if throw_if_fail:
        raise QueryFailure(f"Subqueries failed on all {max_repeats} repetitions")
    else:
        return fail_value
