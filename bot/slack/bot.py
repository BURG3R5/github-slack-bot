"""
Contains the `SlackBot` class, to handle all Slack-related features.

Important methods—
* `.inform` to notify channels about events,
* `.run` to execute slash commands.
"""

from typing import Optional

from ..utils.log import Logger
from .messenger import Messenger
from .runner import Runner


class SlackBot(Messenger, Runner):
    """
    Class providing access to all functions required by the Slack portion of the project.

    Specifics are delegated to parent classes `Messenger` and `Runner`.
    """

    def __init__(
        self,
        *,
        token: str,
        logger: Logger,
        base_url: str,
        secret: str,
    ):
        Messenger.__init__(self, token)
        Runner.__init__(self, logger, base_url, secret)
