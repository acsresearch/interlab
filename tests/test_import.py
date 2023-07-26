import importlib
from pathlib import Path

import pytest
import interlab

P0 = Path(interlab.__path__[0])
MODS = ["interlab."+str((p.relative_to(P0)).with_suffix('')).replace("/",".") for p in P0.glob("**/*.py")]

@pytest.mark.parametrize("module_name", MODS)
def test_import(module_name):
    importlib.import_module(module_name)