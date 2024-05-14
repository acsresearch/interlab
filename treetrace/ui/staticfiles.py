import importlib.resources as resources
import os

from . import browser


PATH_TO_STATIC_FILES = os.path.dirname(resources.files(browser).joinpath("assets"))


def get_current_js_and_css_filenames():
    filenames = os.listdir(os.path.join(PATH_TO_STATIC_FILES, "assets"))
    js = [filename for filename in filenames if filename.endswith(".js")]
    assert len(js) == 1
    css = [filename for filename in filenames if filename.endswith(".css")]
    assert len(css) == 1
    return js[0], css[0]
