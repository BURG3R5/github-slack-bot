from bot.storage import GithubStorage


class GitHubBase:
    """
    Class containing common attributes for `Authenticator` and `Parser`
    """

    def __init__(self):
        self.storage = GithubStorage()
