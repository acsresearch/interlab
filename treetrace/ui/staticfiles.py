import importlib.resources as resources
import os

from . import browser

with resources.path(browser, ".") as static_path:
    PATH_TO_STATIC_FILES = static_path


def get_current_js_and_css_filenames():
    filenames = os.listdir(os.path.join(PATH_TO_STATIC_FILES, "assets"))
    js = [filename for filename in filenames if filename.endswith(".js")]
    assert len(js) == 1
    css = [filename for filename in filenames if filename.endswith(".css")]
    assert len(css) == 1
    return js[0], css[0]
