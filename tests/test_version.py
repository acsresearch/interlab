import subprocess

from interlab import __version__


def test_version():
    poetry_ver = subprocess.getoutput("poetry version").strip().split(" ")[1]
    print(f"poetry version: {poetry_ver!r}")
    print(f"__version__: {__version__!r}")
    assert __version__ == poetry_ver
