from typing import Optional


class Ref:
    def __init__(self, name: str, ref_type: str = "branch", **kwargs):
        self.name = name
        self.link: Optional[str] = kwargs.get("link", None)
        self.type = ref_type
