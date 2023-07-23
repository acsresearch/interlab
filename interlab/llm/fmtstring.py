from __future__ import annotations

import copy
import re
import string
from dataclasses import dataclass
from html import escape as _esc
from typing import Any
from functools import cache
from ..utils import pseudo_random_color

_formatter = string.Formatter()


@dataclass
class _SubFmtString:
    field_name: str
    field_format_spec: str
    value: str | FmtString
    color: str | None = None

    def into_html(self, level: int) -> str:
        color = self.color or pseudo_random_color(
            self.field_name, saturation=0.8, value=0.5
        )
        if isinstance(self.value, FmtString):
            inner = self.value.into_html(level + 1)
        else:
            assert isinstance(self.value, str)
            inner = _esc(self.value)
        # TODO: Add color shade (fg and/or bg) according to level
        return f'<span style="color: {_esc(color)}" data-field-name="{_esc(self.field_name)}" class="FmtString__sub">{inner}</span>'


@dataclass
class _FmtField:
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


class FmtString:
    """
    A partially-formatted string that remembers the substitutions made (incl. nesting). Immutable.
    """

    parts: list[str | _SubFmtString | _FmtField]
    text: str

    def __init__(self, fstr: str | None, _parts=None, _text=None):
        if _parts is not None:
            assert fstr is None
            self.parts = tuple(_parts)
            self.text = _text
            if self.text is None:
                self.text = self._gen_text()
        else:
            assert fstr is not None
            self.parts = tuple(self._parse_fstring(fstr))
            self.text = fstr
        self._initialized = True

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            raise TypeError(f"Instances of {self.__class__.__name__} are immutable")
        return super().__setattr__(name, value)

    def into_html(self, level=0) -> str:
        ps = [p if isinstance(p, str) else p.into_html(level) for p in self.parts]
        return f'<span class="FmtString__span" style="white-space: pre-wrap;">{"".join(ps)}</span>'

    def __log__(self):
        return {"_type": "$html", "html": self.into_html()}

    @classmethod
    def _parse_fstring(cls, fstr: str) -> list[str | _SubFmtString | _FmtField]:
        """Split a given string into"""
        res = []
        for literal_text, field_name, format_spec, conversion in _formatter.parse(fstr):
            if literal_text:
                res.append(literal_text)
            if field_name is not None:
                if not field_name or field_name.isnumeric():
                    raise ValueError(f"Position-based format arguments are unsupported")
                if "{" in format_spec:
                    raise ValueError(
                        f"Format specifiers with arguments unsupported in {cls.__name__}"
                    )
                res.append(
                    _FmtField(
                        field_name=field_name,
                        format_spec=format_spec,
                        conversion=conversion,
                    )
                )
        return res

    def __str__(self) -> str:
        return self.text

    def _gen_text(self) -> str:
        """Generate the underlying (partially formatted) string"""
        res = []
        for p in self.parts:
            if isinstance(p, str):
                res.append(p)
            elif isinstance(p, _FmtField):
                res.append("{" + p.field_format_spec + "}")
            elif isinstance(p, _SubFmtString):
                res.append(str(p.value))
            else:
                assert False
        return "".join(res)

    def format(self, _recursive=False, _partial=True, **kwargs) -> "FmtString":
        assert _recursive is True or _recursive is False
        assert _partial is True or _partial is False

        res = []
        for p in self.parts:
            if isinstance(p, str):
                res.append(p)
            elif isinstance(p, _SubFmtString):
                p2 = copy.copy(p)
                if _recursive:
                    p2.value = p.value.format(
                        _recursive=_recursive, _partial=_partial, **kwargs
                    )
                res.append(p2)
            elif isinstance(p, _FmtField):
                if p.field_name in kwargs:
                    v = kwargs[p.field_name]
                    if p.conversion:
                        v = _formatter.convert_field(v, p.conversion)
                    if p.format_spec:
                        v = _formatter.format_field(v, p.format_spec)
                    # In case v is not already a string or FmtString
                    if not isinstance(v, (FmtString, str)):
                        v = str(v)
                    res.append(
                        _SubFmtString(
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
        return FmtString(None, _parts=res)

    def free_params(self, _recursive=False) -> set[str]:
        """Return names of all free parameters"""
        res = set()
        for p in self.parts:
            if isinstance(p, _FmtField):
                res.add(p.field_name)
            if isinstance(p, _SubFmtString) and _recursive:
                res.update(p.value.free_params(_recursive=_recursive))
        return res
