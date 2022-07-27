"""
Model for a GitHub user.
"""


class User:
    """
    Model for a GitHub user.

    :param name: Username/id of the user.
    :keyword link: Link to the user's GitHub profile.
    """

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.link = kwargs.get("link", f"https://github.com/{name}")

    def __str__(self):
        return f"<{self.link}|{self.name}>"
