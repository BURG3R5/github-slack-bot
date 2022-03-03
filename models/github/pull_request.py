"""
Model for a GitHub PR.
"""


class PullRequest:
    """
    Model for a GitHub PR.

    :param title: Title of the PR.
    :param number: PR number.
    :param link: Link to the PR.
    """

    def __init__(self, title: str, number: int, link: str):
        self.title = title
        self.number = number
        self.link = link

    def __str__(self):
        return f"<{self.link}|#{self.number} {self.title}>"
