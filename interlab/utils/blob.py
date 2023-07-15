import base64


class Blob:
    def __init__(self, data: bytes, mime_type: str = "application/octet-stream"):
        self.data = data
        self.mime_type = mime_type

    def __log__(self):
        return {
            "data": base64.b64encode(self.data).decode(),
            "mime_type": self.mime_type,
        }