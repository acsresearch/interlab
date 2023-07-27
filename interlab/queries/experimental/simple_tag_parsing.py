import re

from ...queries import ParsingFailure


def parse_tag(tag: str, text: str, required=False, parse=None) -> str | None:
    if len(re.findall(f"<{tag}>", text)) > 1 or len(re.findall(f"</{tag}>", text)) > 1:
        raise ParsingFailure(
            f"Multiple occurences of '<{tag}>' or '</{tag}>' found in parsed text"
        )
    r = re.search(f"<{tag}>(.*)</{tag}>", text, re.MULTILINE | re.DOTALL)
    if not r or not r.groups():
        if required:
            raise ParsingFailure(f"Tags '<{tag}>...</{tag}>' not found in parsed text")
        return None
    res = r.groups()[0]
    if parse is not None:
        try:
            res = parse(res)
        except ValueError:
            raise ParsingFailure(
                f"Failed parsing value of '<{tag}>...</{tag}>' with {parse!r}"
            )
    return res
