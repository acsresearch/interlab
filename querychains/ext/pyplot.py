from ..blob import Blob


def capture_figure(file_format: str = "png", **kwargs):
    import matplotlib.pyplot as plt
    import io

    buf = io.BytesIO()
    plt.savefig(buf, format=file_format, **kwargs)
    buf.seek(0)
    if file_format == "png":
        mime = "image/png"
    else:
        mime = None
    return Blob(buf.read(), mime_type=mime)