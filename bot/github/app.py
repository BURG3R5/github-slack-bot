"""
Contains the `GitHubApp` class, to handle all GitHub-related features.

Important methods—
* `.verify` to verify incoming events,
* `.parse` to cast event payload into a GitHubEvent,
* `.redirect_to_oauth_flow` to initiate GitHub OAuth flow,
* `.set_up_webhooks` to set up GitHub webhooks in a repo.
"""

from .authenticator import Authenticator
from .parser import Parser


class GitHubApp(Authenticator, Parser):
    """
    Class providing access to all functions required by the GitHub portion of the project.

    Specifics are delegated to parent classes `Authenticator` and `Parser`.
    """

    def __init__(
        self,
        *,
        base_url: str,
        client_id: str,
        client_secret: str,
    ):
        Authenticator.__init__(self, base_url, client_id, client_secret)
        Parser.__init__(self)
