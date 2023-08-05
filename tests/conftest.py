import os
import sys

import pytest

TESTS_DIR = os.path.abspath(".")
ROOT_DIR = os.path.dirname(TESTS_DIR)

sys.path.insert(0, ROOT_DIR)


@pytest.fixture
def storage(tmpdir):
    from interlab.context import FileStorage

    return FileStorage(os.path.join(tmpdir, "storage"))
