"""
Model for a Git commit.
"""


class Commit:
    """
    Model for a Git commit.

    :param message: The commit message.
    :param sha: The commit's SHA.
    :param link: The commit's link on GitHub.
    """

    def __init__(
        self,
        message: str,
        sha: str,
        link: str,
    ):
        self.message = message
        self.sha = sha
        self.link = link

    def __str__(self) -> str:
        return f"<{self.message}|{self.link}>"
