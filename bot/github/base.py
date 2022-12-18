from bot.storage import SecretStorage


class GitHubBase:
    """
    Class containing common attributes for `Authenticator` and `Parser`
    """

    def __init__(self):
        self.storage = SecretStorage()
