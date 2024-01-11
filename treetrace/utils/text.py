import random
import re
import string
from datetime import datetime

UID_CHARS = string.ascii_lowercase + string.ascii_uppercase + string.digits
ESCAPE_NAME_RE = re.compile("[^0-9a-zA-Z]+")
UID_CHECK_REGEXP = re.compile(r"^[a-z0-9A-Z:\-\._]+$")
ESCAPE_DATE_RE = re.compile(r"[:/\\]")


def shorten_str(s: str | None, max_len=32) -> str:
    if s is None:
        return "None"
    r = repr(s)
    if len(r) <= max_len:
        return r
    return r[: max_len - 5] + "[...]"


def generate_uid(name: str) -> str:
    name = ESCAPE_NAME_RE.sub("_", name[:16])
    random_part = "".join(random.choice(UID_CHARS) for _ in range(6))
    # Replace ':' to appease windows, and also both slashes just in case
    date = ESCAPE_DATE_RE.sub("-", datetime.now().isoformat(timespec="seconds"))
    return f"{date}-{name}-{random_part}"


def validate_uid(uid: str) -> bool:
    return bool(UID_CHECK_REGEXP.match(uid))
