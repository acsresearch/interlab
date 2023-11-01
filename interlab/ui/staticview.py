import json
import uuid

from interlab.context import Context
from interlab.ui.staticfiles import get_current_js_and_css_filenames

JS_FILE, CSS_FILE = get_current_js_and_css_filenames()
CDN_VERSION = "5464935062082e96e24a95cda009e5419ce09a51"  # In future, it should match the released version
CDN_URL = f"https://cdn.jsdelivr.net/gh/acsresearch/interlab@{CDN_VERSION}/interlab/ui/browser/assets/"

# ONLY FOR LOCAL TESTING
# CDN_URL = f"http://localhost:2000/"

STATIC_CONTEXT_TEMPLATE_HTML = """
<div id={id}></div>
<script src="{cdn_url}{js_file}"></script>
<link rel="stylesheet" href="{cdn_url}{css_file}">
<script>
import("{cdn_url}{js_file}").then(() => window.initInterlab("{id}", {context}))
</script>
"""


STATIC_CONTEXT_TEMPLATE_PAGE = """<!doctype html>
    <html lang="en">
    <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Interlab Browser</title>
</head>
<body>
{html}
</body>
</html>"""


def create_context_static_html(context: Context) -> str:
    context_json = json.dumps(context.to_dict())
    return STATIC_CONTEXT_TEMPLATE_HTML.format(
        context=context_json,
        id=uuid.uuid4(),
        cdn_url=CDN_URL,
        js_file=JS_FILE,
        css_file=CSS_FILE,
    )


def create_context_static_page(context: Context) -> str:
    html = create_context_static_html(context)
    return STATIC_CONTEXT_TEMPLATE_PAGE.format(html=html)
