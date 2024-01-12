from typing import Awaitable, Callable

from treetrace import TracingNode

from ...queries import QueryFailure


def repeat_on_failure(
    fn: Callable, max_repeats=3, with_tracing=True, throw_if_fail=True, fail_value=None
):
    for i in range(max_repeats):
        try:
            if with_tracing:
                name = f"{fn.__name__}: {i + 1}/{max_repeats}"
                with TracingNode(name=name, kind="repeat_on_failure") as c:
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
    fn: Awaitable, max_repeats=3, with_tracing=True, throw_if_fail=True, fail_value=None
):
    for i in range(max_repeats):
        try:
            if with_tracing:
                name = f"{i + 1}/{max_repeats}"
                with TracingNode(name=name, kind="async_repeat_on_failure") as c:
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
