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
