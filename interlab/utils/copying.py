import copy
import tracemalloc
import warnings
from typing import Any


class ImmutableWrapper:
    """
    A semi-transparent wrapper for immutable objects, preventing needless copying.

    This class wraps an object and proxies all method calls to the wrapped object,
    including indexing and calling.

    Note that the proxying does not aim to be perfectly transparent but merely
    practiacal for most purposes. If you need specific behavior, you can create your
    own wrapper of a specific type, overriding `__deepcopy__` and any other methods you need.
    """

    def __init__(self, obj: Any):
        self._ImmutableWrapper_obj = obj

    def __deepcopy__(self, _memo):
        return self

    def __getattr__(self, key):
        if key == "_ImmutableWrapper_obj":
            super().__getattr__(key)
        else:
            return getattr(self._ImmutableWrapper_obj, key)

    def __setattr__(self, key, value):
        if key == "_ImmutableWrapper_obj":
            super().__setattr__(key, value)
        else:
            setattr(self._ImmutableWrapper_obj, key, value)

    def __delattr__(self, key):
        assert key != "_ImmutableWrapper_obj"
        delattr(self._ImmutableWrapper_obj, key)

    def __getitem__(self, key):
        return self._ImmutableWrapper_obj[key]

    def __setitem__(self, key, value):
        self._ImmutableWrapper_obj[key] = value

    def __delitem__(self, key):
        del self._ImmutableWrapper_obj[key]

    def __call__(self, *args, **kwargs):
        return self._ImmutableWrapper_obj(*args, **kwargs)


DEEPCOPY_WARN_LIMIT = 8 * 1 << 20  # 8 MB
"""
Limit for warning about deepcopies of large objects in InterLab.

You can change the limit globally at any time.
To disable checking for the memory used by deepcopy, set to `None`.
"""


def checked_deepcopy(obj: Any, limit: int | str | None = "default") -> Any:
    """
    Perform a deep copy of the object, checking for unexpected memory usage.

    This function calls `copy.deepcopy` while checking for a large increase in memory usage.
    The limit for the memory increase can be set globally by changing the value of `DEEPCOPY_WARN_LIMIT`
    or by setting the `limit` parameter; set either to `None` to switch off the check.
    If the limit is exceeded, a `UserWarning` is raised. Note that in multi-threaded applications,
    this warning may also be caused by large allocations in other threads coincidental with the deepcopy.

    **Note on avoiding costly copies:** By default, copying uses `copy.deepcopy`.
    If your are holding large objects that are effectively immutable (i.e. are guaranteed not to be
    modified during their usage), you can override their copying behavior to save time and memory by one of:

    * Overriding the `__deepcopy__` method of the immutable object (returning the same object).
    * Wrapping the object in `ImmutableWrapper` that proxies all method calls to the original object
      but avoids deep-copying. Note this changes the type of the wrapped object; see the docs of
      `ImmutableWrapper` for details on typing.
    * Overriding the `__deepcopy__` method of the holder of the object. This is most general but may be
      complicated e.g. in subclasses of the holder.
    """

    if limit == "default":
        limit = DEEPCOPY_WARN_LIMIT
    if limit is None:
        # No limit checking
        return copy.deepcopy(obj)

    tracemalloc.start()
    mem0 = tracemalloc.get_traced_memory()[0]
    try:
        return copy.deepcopy(obj)
    finally:
        mem1 = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()
        if mem1 - mem0 >= limit:
            warnings.warn(
                f"Deepcopy of {obj} used {mem1 - mem0} bytes of memory. Make sure you are not copying large objects "
                "unnecessarily. See the documentation of `checked_deepcopy` for details. Note that in "
                "multi-threaded applications, this may also be caused by large allocations in other threads "
                "coincidental with the deepcopy."
            )
