class Html:
    def __init__(self, html: str):
        self.html = html

    def __log__(self):
        return {"_type": "$html", "html": self.html}
