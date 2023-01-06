from ..storage import MockSubscriptionStorage


class MockSlackBotBase:
    """
    Mock class containing common attributes for `TestableMessenger` and `TestableRunner`
    """

    def __init__(self, _: str):
        self.storage = MockSubscriptionStorage()
        self.client = None
