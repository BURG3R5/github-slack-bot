class Link:
    def __init__(self, url: str | None = None, text: str | None = None):
        self.url = url
        self.text = text

    def __str__(self) -> str:
        return f"<{self.url}|{self.text}>"
