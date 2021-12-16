from typing import Optional


class Repository:
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.link: Optional[str] = kwargs.get("link", None)
