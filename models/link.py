from typing import Optional


class Link:
    def __init__(self, url: Optional[str] = None, text: Optional[str] = None):
        self.url = url
        self.text = text

    def __str__(self) -> str:
        return f"<{self.url}|{self.text}>"
