class Html:
    def __init__(self, html: str):
        self.html = html

    def __log__(self):
        return {"html": self.html}
