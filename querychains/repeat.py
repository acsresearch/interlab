from .context import with_new_context
from .utils import QueryFailure
from .data import IntoData


def repeat_on_failure(fn, input: IntoData, max_repeats=3) -> IntoData:
    for i in range(max_repeats):
        try:
            return with_new_context("repeated_on_failure", fn, input)
        except QueryFailure as exc:
            if i == max_repeats - 1:
                raise QueryFailure(f"Subqueries failed on all {i} repetitions") from exc
