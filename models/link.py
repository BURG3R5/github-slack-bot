"""
Contains the `Link` model.

This was separated from "slack.py" To prevent circular-import error.
"""


class Link:
    """
    Holds a text string and a URL.
    Has an overridden __str__ method to make posting links on Slack easier.

    :param url: URL that the link should lead to.
    :param text: Text that should be displayed instead of the link.
    """

    def __init__(self, url: str = "", text: str = ""):
        self.url = url
        self.text = text

    def __str__(self) -> str:
        """
        Overridden object method for pretty-printing links.
        :return: String formatted like a proper Slack link.
        """
        return f"<{self.url}|{self.text}>"
