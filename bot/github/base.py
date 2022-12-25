from bot.storage import GitHubStorage


class GitHubBase:
    """
    Class containing common attributes for `Authenticator` and `Parser`
    """

    def __init__(self):
        self.storage = GitHubStorage()
