from __future__ import annotations

import copy
import string
from dataclasses import dataclass
from html import escape as _esc
from typing import Any, Iterable

from ..utils import pseudo_random_color

_formatter = string.Formatter()


@dataclass
class _SubFormatStr:
    field_name: str
    field_format_spec: str
    value: str | FormatStr
    color: str | None = None

    def into_html(self, level: int) -> str:
        color = self.color or pseudo_random_color(
            self.field_name, saturation=0.8, value=0.5
        )
        if isinstance(self.value, FormatStr):
            inner = self.value.into_html(level + 1)
        else:
            assert isinstance(self.value, str)
            inner = _esc(self.value)
        # TODO: Add color shade (fg and/or bg) according to level
        return (
            f'<span style="color: {_esc(color)}" data-field-name="{_esc(self.field_name)}" '
            f'class="FmtString__sub">{inner}</span>'
        )


@dataclass
class _FormatStrField:
    field_name: str
    format_spec: str | None
    conversion: str | None
    field_format_spec: str | None = None
    color: str | None = None

    def __post_init__(self):
        if self.field_format_spec is None:
            self.field_format_spec = self.field_name
            if self.conversion:
                self.field_format_spec += f"!{self.conversion}"
            if self.format_spec:
                self.field_format_spec += f":{self.format_spec}"

    def into_html(self, level: int) -> str:
        color = _esc(self.color or "#e40000")
        inner = _esc("{" + self.field_format_spec + "}")
        return f'<span style="color: {color}" class="FmtString__field">{inner}</span>'


class FormatStr:
    """
    A partially-formatted string that remembers the substitutions made (incl. nesting). Immutable.
    """

    _parts: list[str | _SubFormatStr | _FormatStrField]
    _text: str

    def __init__(self, fstr: str | None, _parts=None, _text=None):
        if _parts is not None:
            assert fstr is None
            self._parts = tuple(_parts)
            self._text = _text
            if self._text is None:
                self._text = self._gen_text()
        else:
            assert fstr is not None
            self._parts = tuple(self._parse_fstring(fstr))
            self._text = fstr
        self._initialized = True

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            raise TypeError(f"Instances of {self.__class__.__name__} are immutable")
        return super().__setattr__(name, value)

    def into_html(self, level=0) -> str:
        ps = [p if isinstance(p, str) else p.into_html(level) for p in self._parts]
        return f'<span class="FmtString__span" style="white-space: pre-wrap;">{"".join(ps)}</span>'

    def __log__(self):
        return {"_type": "$html", "html": self.into_html()}

    @classmethod
    def _parse_fstring(cls, fstr: str) -> list[str | _SubFormatStr | _FormatStrField]:
        """Split a given string into"""
        res = []
        for literal_text, field_name, format_spec, conversion in _formatter.parse(fstr):
            if literal_text:
                res.append(literal_text)
            if field_name is not None:
                if not field_name or field_name.isnumeric():
                    raise ValueError("Position-based format arguments are unsupported")
                if "{" in format_spec:
                    raise ValueError(
                        f"Format specifiers with arguments unsupported in {cls.__name__}"
                    )
                res.append(
                    _FormatStrField(
                        field_name=field_name,
                        format_spec=format_spec,
                        conversion=conversion,
                    )
                )
        return res

    def __str__(self) -> str:
        return self._text

    def _gen_text(self) -> str:
        """Generate the underlying (partially formatted) string"""
        res = []
        for p in self._parts:
            if isinstance(p, str):
                res.append(p)
            elif isinstance(p, _FormatStrField):
                res.append("{" + p.field_format_spec + "}")
            elif isinstance(p, _SubFormatStr):
                res.append(str(p.value))
            else:
                assert False
        return "".join(res)

    def __add__(self, other: str | FormatStr) -> FormatStr:
        parts = list(self._parts)
        if isinstance(other, str):
            parts.append(other)
        elif isinstance(other, FormatStr):
            parts.extend(other._parts)
        else:
            raise TypeError(
                f"{self.__class__.__name__}.__add__() only accepts str and FormatStr, got {type(other)}"
            )
        return self.__class__(None, _parts=parts)

    def join(self, iter: Iterable[str | FormatStr]) -> FormatStr:
        parts = []
        for i, s in enumerate(iter):
            if i > 0:
                parts.extend(self._parts)
            if isinstance(s, str):
                parts.append(s)
            elif isinstance(s, FormatStr):
                parts.extend(s._parts)
            else:
                raise TypeError(
                    f"{self.__class__.__name__}.join() only accepts str and FormatStr, got {type(s)}"
                )
        return self.__class__(None, _parts=parts)

    def format(self, _recursive=False, _partial=True, **kwargs) -> "FormatStr":
        assert _recursive is True or _recursive is False
        assert _partial is True or _partial is False

        res = []
        for p in self._parts:
            if isinstance(p, str):
                res.append(p)
            elif isinstance(p, _SubFormatStr):
                p2 = copy.copy(p)
                if _recursive:
                    p2.value = p.value.format(
                        _recursive=_recursive, _partial=_partial, **kwargs
                    )
                res.append(p2)
            elif isinstance(p, _FormatStrField):
                if p.field_name in kwargs:
                    v = kwargs[p.field_name]
                    if p.conversion:
                        v = _formatter.convert_field(v, p.conversion)
                    if p.format_spec:
                        v = _formatter.format_field(v, p.format_spec)
                    # In case v is not already a string or FmtString
                    if not isinstance(v, (FormatStr, str)):
                        v = str(v)
                    res.append(
                        _SubFormatStr(
                            field_name=p.field_name,
                            field_format_spec=p.field_format_spec,
                            value=v,
                            color=p.color,
                        )
                    )
                else:
                    if not _partial:
                        raise KeyError(p.field_name)
                    res.append(p)
        return FormatStr(None, _parts=res)

    def free_params(self, _recursive=False) -> set[str]:
        """Return names of all free parameters"""
        res = set()
        for p in self._parts:
            if isinstance(p, _FormatStrField):
                res.add(p.field_name)
            if isinstance(p, _SubFormatStr) and _recursive:
                res.update(p.value.free_params(_recursive=_recursive))
        return res
