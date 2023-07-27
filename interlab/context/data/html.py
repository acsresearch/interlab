class Html:
    def __init__(self, html: str):
        self.html = html

    def __log_to_context__(self):
        return {"_type": "$html", "html": self.html}
