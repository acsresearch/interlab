import os
import sys

import pytest

TESTS_DIR = os.path.abspath(".")
ROOT_DIR = os.path.dirname(TESTS_DIR)

sys.path.insert(0, ROOT_DIR)

from interlab.tracing import FileStorage  # noqa E402


@pytest.fixture
def storage(tmpdir):
    return FileStorage(os.path.join(tmpdir, "storage"))
