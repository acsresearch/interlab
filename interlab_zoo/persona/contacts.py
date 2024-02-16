from typing import Sequence

from .personas import Persona


def link(personas: Sequence[Persona]):
    for p1 in personas:
        for p2 in personas:
            if p1 == p2:
                continue
            p1.observe(f"You are in contact with {p2.name}: {p2.public_info(p1)}")
