import random
import re
import string
from datetime import datetime

UID_CHARS = string.ascii_lowercase + string.ascii_uppercase + string.digits
ESCAPE_NAME_RE = re.compile("[^0-9a-zA-Z]+")
UID_CHECK_REGEXP = re.compile(r"^[a-z0-9A-Z:\-\._]+$")


def shorten_str(s: str | None, max_len=32) -> str:
    if s is None:
        return "None"
    r = repr(s)
    if len(r) <= max_len:
        return r
    return r[: max_len - 5] + "[...]"


def short_repr(obj: object) -> str:
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


def validate_uid(uid: str) -> bool:
    return bool(UID_CHECK_REGEXP.match(uid))


def replace(text, replaces):
    for name, value in replaces.items():
        text = text.replace(name, value)
    return text


def ensure_newline(text: str, count=1) -> str:
    c = 0
    while (len(text) - c - 1) >= 0 and text[len(text) - c - 1] == "\n":
        c += 1
    if c >= count:
        return text
    return text + "\n" * (count - c)


def group_newlines(text: str, max_nexlines=2) -> str:
    return re.sub(f"( *\n){{{max_nexlines+1},}}", "\n" * max_nexlines, text, flags=re.M)


def remove_leading_spaces(text: str) -> str:
    text = re.sub("^[\t ]+", "", text, flags=re.M)  # First line is special
    return re.sub("\n[\t ]+", "", text, flags=re.M)
