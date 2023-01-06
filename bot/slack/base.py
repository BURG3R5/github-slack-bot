from slack.web.client import WebClient

from bot.storage import SubscriptionStorage


class SlackBotBase:
    """
    Class containing common attributes for `Messenger` and `Runner`
    """

    def __init__(self, token: str):
        self.storage = SubscriptionStorage()
        self.client: WebClient = WebClient(token)
