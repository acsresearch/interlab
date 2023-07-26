import IPython.display


def detect_colab():
    try:
        import google.colab  # noqa: F401

        return True
    except ModuleNotFoundError:
        return False


def iframe_for_port(port, width="95%", height=600):
    return IPython.display.Javascript(
        """
            (async ()=>{
                fm = document.createElement('iframe')
                fm.src = await google.colab.kernel.proxyPort(%s)
                fm.width = '%s'
                fm.height = '%s'
                fm.frameBorder = 0
                fm.style = 'background: white;'
                document.body.append(fm)
            })();
            """
        % (port, width, height)
    )
