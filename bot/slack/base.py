from bot.storage import SubscriptionStorage


class SlackBotBase:
    """
    Class containing common attributes for `Messenger` and `Runner`
    """

    def __init__(self):
        self.storage = SubscriptionStorage()
