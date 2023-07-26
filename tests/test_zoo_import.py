import importlib
from pathlib import Path

import pytest

import interlab_zoo

P0 = Path(interlab_zoo.__path__[0])
MODS = [
    "interlab_zoo." + str((p.relative_to(P0)).with_suffix("")).replace("/", ".")
    for p in P0.glob("**/*.py")
]


@pytest.mark.parametrize("module_name", MODS)
def test_import(module_name):
    importlib.import_module(module_name)
