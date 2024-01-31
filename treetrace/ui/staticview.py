import json
import uuid

from ..tracing.tracingnode import TracingNode
from .staticfiles import get_current_js_and_css_filenames

JS_FILE, CSS_FILE = get_current_js_and_css_filenames()
CDN_VERSION = "9fbc2169cd64cac537b74c432a6d1a7a2b7e8b0c"
CDN_URL = f"https://cdn.jsdelivr.net/gh/acsresearch/interlab@{CDN_VERSION}/treetrace/ui/browser/assets/"

# ONLY FOR LOCAL TESTING
# CDN_URL = f"http://localhost:2000/"

STATIC_NODE_TEMPLATE_HTML = """
<div id="{id}"></div>
<script src="{cdn_url}{js_file}"></script>
<link rel="stylesheet" href="{cdn_url}{css_file}">
<script>
import("{cdn_url}{js_file}").then(() => window.initTreeTraceBrowser("{id}", {tracing_node}))
</script>
"""


STATIC_NODE_TEMPLATE_PAGE = """<!doctype html>
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


def create_node_static_html(node: TracingNode) -> str:
    node_json = json.dumps(node.to_dict())
    return STATIC_NODE_TEMPLATE_HTML.format(
        tracing_node=node_json,
        id=uuid.uuid4(),
        cdn_url=CDN_URL,
        js_file=JS_FILE,
        css_file=CSS_FILE,
    )


def create_node_static_page(node: TracingNode) -> str:
    html = create_node_static_html(node)
    return STATIC_NODE_TEMPLATE_PAGE.format(html=html)
