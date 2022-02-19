"""
Model for a GitHub repository.
"""


class Repository:
    """
    Model for a GitHub repository.

    :param name: Name of the repo.
    :param link: Link to the repo on GitHub.
    """

    def __init__(self, name: str, link: str):
        self.name = name
        self.link = link

    def __str__(self):
        return f"<{self.link}|{self.name}>"
