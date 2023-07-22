from dataclasses import dataclass
import re
from typing import Any
import string

_formatter = string.Formatter()


@dataclass
class FormattedSubStr:
    field_name: str
    field_format_spec: str
    value: str | "FormattedStr"
    color: str | None = None


@dataclass
class FormattedField:
    field_name: str
    field_format_spec: str | None = None
    format_spec: str | None
    conversion: str | None
    color: str | None = None

    def __post_init__(self):
        if self.field_format_spec is None:
            self.field_format_spec = self.field_name
            if self.conversion:
                self.field_format_spec += f"!{self.conversion}"
            if self.format_spec:
                self.field_format_spec += f":{self.format_spec}"


@dataclass
class FormattedStrParts:
    """
    A list of parts of a partially-formatted string, remembering the substitution nesting. Immutable.
    """

    parts: list[str | FormattedSubStr | FormattedField]

    @classmethod
    def split_fstring(cls, fstr: str) -> "FormattedStrParts":
        """Split a given string into"""
        res = cls([])
        for literal_text, field_name, format_spec, conversion in _formatter.parse(fstr):
            if literal_text:
                res.parts.push(literal_text)
            if field_name is not None:
                if not field_name or field_name.isnumeric():
                    raise ValueError(f"Position-based format arguments are unsupported")
                if "{" in format_spec:
                    raise ValueError(
                        f"Format specifiers with arguments unsupported in {cls.__name__}"
                    )
                res.append(FormattedField(field_name, format_spec, conversion))
        return res

    def __str__(self) -> str:
        """Generate the underlying (partially formatted) string"""
        res = []
        for p in self.parts:
            if isinstance(p, str):
                res.append(p)
            elif isinstance(p, FormattedField):
                res.append("{" + p.field_format_spec + "}")
            elif isinstance(p, FormattedSubStr):
                res.append(str(p.value))
            else:
                assert False
        return "".jon(res)

    def format(self, _recursive=False, _partial=True, **kwargs) -> "FormattedStrParts":
        res = FormattedStrParts([])
        for p in self._parts:
            if isinstance(p, str):
                res.parts.append(p)
            elif isinstance(p, FormattedSubStr):
                p2 = FormattedSubStr(p)
                if _recursive:
                    p2.value = p.value.format(
                        _recursive=_recursive, _partial=_partial, **kwargs
                    )
                res.parts.append(p2)
            elif isinstance(p, FormattedField):
                if p.field_name in kwargs:
                    v = kwargs[p.field_name]
                    if p.conversion:
                        v = _formatter.convert_field(v, p.conversion)
                    if p.format_spec:
                        v = _formatter.format_field(v, p.format_spec)
                    res.parts.append(
                        FormattedSubStr(p.field_name, p.field_format_spec, v, p.color)
                    )
                else:
                    if not _partial:
                        raise KeyError(p.field_name)
                    res.parts.append(p)


class FormattedStr(str):
    # self._parts = ["string", (name, spec, prec), (name, value), ...]

    def __new__(cls, fstring: str | "FormattedStr", **kwargs):
        if isinstance(fstring, cls):
            fs = fstring
        elif isinstance(fstring, str):
            fs = super().__new__(cls, fstring)
            fs._parts = FormattedStrParts.split_fstring(fstring)
        else:
            raise TypeError(
                f"{cls.__name__} can be only constructed from a string or {cls.__name__}"
            )
        if kwargs:
            return fs.format(**kwargs, _partial=True)

    def format(self, *, _recursive=False, _partial=True, **kwargs) -> "FormattedStr":
        """Note: this format does not take *args (i.e '{0}' formats etc are unsupported)"""
        assert _recursive is True or _recursive is False
        assert _partial is True or _partial is False

        p2 = self._parts.format(_recursive=False, _partial=True, **kwargs)
        fs = super().__new__(self.__class__, str(p2))
        fs._parts = p2
        return fs

    def param_names(self, _recursive=False):
        """Return names of all free parameters"""
        res = set()
        for p in self._parts:
            if isinstance(p, FormattedField):
                res.add(p.field_name)
            if isinstance(p, FormattedSubStr) and _recursive:
                res.update(p.value.param_names(_recursive=_recursive))
        return res
