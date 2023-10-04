from ..context.data.blob import DataWithMime


def capture_figure(figure=None, file_format: str = "png", **kwargs):
    import io

    import matplotlib.pyplot as plt

    buf = io.BytesIO()
    plt.savefig(buf, format=file_format, **kwargs)
    buf.seek(0)
    if figure:
        plt.close(figure)
    if file_format == "png":
        mime = "image/png"
    else:
        mime = None
    return DataWithMime(buf.read(), mime_type=mime)
