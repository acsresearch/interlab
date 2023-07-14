import re


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
