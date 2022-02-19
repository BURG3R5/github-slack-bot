"""
Model for a GitHub issue.
"""


class Issue:
    """
    Model for a GitHub issue.

    :param title: Title of the issue.
    :param number: Issue number.
    :param link: Link to the issue.
    """

    def __init__(self, title: str, number: int, link: str):
        self.title = title
        self.number = number
        self.link = link

    def __str__(self):
        return f"<{self.link}|#{self.number} {self.title}>"
