import colorsys
import copy
import random
import re
from typing import Any


class HTMLColor:
    """Helper class representing RGB color. Accepts HTML hex notation (3, 4, 6 or 8 hex digits, with optional '#')."""

    def __init__(self, color: str):
        color = color.strip()
        m = re.fullmatch(r"[#]?([0-9a-f]{3,8})", color.lower())
        if not m:
            raise ValueError(
                f"Invalid color spec: {color!r}, expected HTML hex color spec"
            )
        c = m.groups()[0]
        if len(c) not in (3, 4, 6, 8):
            raise ValueError(
                f"Invalid color spec: {color!r}, expected HTML hex color spec"
            )
        if len(c) <= 4:
            c = "".join(2 * x for x in c)
        self.r = int(c[0:2], base=16)
        self.g = int(c[2:4], base=16)
        self.b = int(c[4:6], base=16)
        if len(c) == 8:
            self.a = int(c[6:8], base=16)
        else:
            self.a = None

    def as_floats(self) -> tuple:
        "Returns (r,g,b) or (r,g,b,a), with all values 0..1"
        cf = (self.r / 255, self.g / 255, self.b / 255)
        if self.a is not None:
            cf += (self.a / 255,)
        return cf

    @classmethod
    def from_floats(cls, r: float, g: float, b: float, a: float = None) -> "HTMLColor":
        """Returns (r,g,b) or (r,g,b,a), with all values 0.0 .. 1.0."""
        c = cls("000000")
        c.r = round(r * 255)
        c.g = round(g * 255)
        c.b = round(b * 255)
        if a is not None:
            c.a = round(a * 255)
        return c

    def __str__(self):
        """Returns the color in '#RRGGBB[AA]' HTML hex format."""
        s = f"#{self.r:02x}{self.g:02x}{self.b:02x}"
        if self.a is not None:
            s += f"{self.a:02x}"
        return s

    def __repr__(self):
        return f"{self.__class__.__name__}({str(self)!r})"

    def copy(self):
        return copy.copy(self)

    def _blend_lightness(self, tgt: float, rate: float) -> "HTMLColor":
        hue, light, sat = colorsys.rgb_to_hls(*self.as_floats())
        light = rate * tgt + (1 - rate) * light
        c = self.from_floats(*colorsys.hls_to_rgb(hue, light, sat))
        c.a = self.a
        return c

    def lighter(self, rate=0.2) -> "HTMLColor":
        "Returns a lighter copy of the color: rate=1.0 returns white, rate=0 returns the same color."
        return self._blend_lightness(1.0, rate)

    def darker(self, rate=0.2) -> "HTMLColor":
        "Returns a darker copy of the color: rate=1.0 returns black, rate=0 returns the same color."
        return self._blend_lightness(0.0, rate)

    def with_alpha(self, a: float) -> "HTMLColor":
        "Returns a copy of the color with given alpha: float 0.0-1.0"
        assert isinstance(a, (float, int)) and a <= 1.0 and a >= 0.0
        c = self.copy()
        c.a = round(a * 255)
        return c

    @classmethod
    def random_color(
        cls,
        seed: Any | None = None,
        saturation=0.7,
        lighness=0.5,
        *,
        vary_lightness_rate=0.2,
        vary_saturation_rate=0.3,
    ) -> str:
        """Returns a pseudo-random color for the given object, or a random color.

        The color is primarily determined by a random hue and given saturation and lightness.
        By default, the lightness and saturation of the generated color slightly varies from the given values.
        The returned color is guaranteed to be stable across runs for string seeds
        (or objects with stable __repr__ value).
        """
        if (seed is not None) and (not isinstance(seed, str)):
            # This can bring instability between versions of your __repr__ or Python
            # and for some objects this may just vary even among identical objects
            seed = repr(seed)
            # Remove any concrete pointer addresses, as these will vary
            seed = re.sub(f"0x[0-9a-fA-F]{8,20}", "<0xPTR>", seed)
        rng = random.Random(seed)

        hue = rng.random()
        tgt_s = rng.random()
        tgt_l = rng.random()
        return cls.from_floats(
            *colorsys.hls_to_rgb(
                hue,
                (1 - vary_lightness_rate) * lighness + vary_lightness_rate * tgt_l,
                (1 - vary_saturation_rate) * saturation + vary_saturation_rate * tgt_s,
            )
        )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (
            (self.r == other.r)
            and (self.g == other.g)
            and (self.b == other.b)
            and (self.a == other.a)
        )
