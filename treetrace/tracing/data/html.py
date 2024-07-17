class Html:
    """
    Wrapper around HTML code that is directly rendered in Data Browser
    """

    def __init__(self, html: str):
        self.html = html

    def __trace_to_node__(self):
        return {"_type": "$html", "html": self.html}
