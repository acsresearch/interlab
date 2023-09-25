def display_iframe(url: str, port: int, width="90%", height=600):
    from IPython.display import IFrame, display

    from interlab.ext.google_colab import detect_colab, iframe_for_port

    if detect_colab():
        display(iframe_for_port(port, width=width, height=height))
    else:
        display(IFrame(url, width=width, height=height))


def display_iframe_html(content: str, width="90%", height=600):
    from IPython.core.display import HTML
    from IPython.display import display

    template = """<iframe
        width="{width}"
        height="{height}"
        frameborder="0"
        allowfullscreen>{content}</iframe>"""
    #html = template.format(width=width, height=height, content=content)
    display(HTML(content))
