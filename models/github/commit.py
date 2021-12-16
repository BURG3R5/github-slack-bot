from typing import Optional


class Commit:
    def __init__(
        self,
        message: Optional[str] = None,
        sha: Optional[str] = None,
        link: Optional[str] = None,
    ):
        self.message = message
        self.sha = sha
        self.link = link
