import colorsys
import logging
import random
import re
import string
from datetime import datetime
from typing import Hashable

from . import blob, data, text  # noqa: F401

LOG = logging.getLogger("interlab")
UID_CHARS = string.ascii_lowercase + string.ascii_uppercase + string.digits
ESCAPE_NAME_RE = re.compile("[^0-9a-zA-Z]+")


class QueryFailure(Exception):
    pass


def shorten_str(s: str | None, max_len=32) -> str:
    if s is None:
        return "None"
    r = repr(s)
    if len(r) <= max_len:
        return r
    return r[: max_len - 5] + "[...]"


def short_repr(obj: any) -> str:
    if isinstance(obj, str):
        s = obj
    else:
        s = repr(obj)
    return shorten_str(s)


def generate_uid(name: str) -> str:
    name = ESCAPE_NAME_RE.sub("_", name[:16])
    random_part = "".join(random.choice(UID_CHARS) for _ in range(6))
    uid = f"{datetime.now().isoformat(timespec='seconds')}-{name}-{random_part}"
    # Replace ':' to appease windows, and also both slashes just in case
    return uid.replace(":/\\", "-")


def pseudo_random_color(seed: Hashable, saturation=0.5, value=1.0) -> str:
    r, g, b = colorsys.hsv_to_rgb((hash(seed) % 256) / 255, saturation, value)
    res = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
    assert len(res) == 7
    return res
