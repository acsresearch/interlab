import subprocess

from interlab.context.data import DataWithMime


def dot_to_png(dot_content: str) -> DataWithMime:
    p = subprocess.Popen(
        ["dot", "-Tpng"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    (stdout, stderr) = p.communicate(dot_content.encode())
    if p.returncode != 0:
        raise Exception(f"Calling 'dot' failed:\n{stderr}")
    return DataWithMime(stdout, mime_type="image/png")
