"""
Contains the `SlackBot` class, to handle all Slack-related features.

Important methods—
* `SlackBot.inform` to notify channels about events,
* `SlackBot.run` to execute slash commands.
"""

from ..models.slack import Channel
from ..utils.log import Logger
from ..utils.storage import Storage
from .messenger import Messenger
from .runner import Runner


class SlackBot(Messenger, Runner):
    """
    Class providing access to all functions required by the Slack portion of the project.

    Specifics are delegated to superclasses `Messenger` and `Runner`.
    """

    subscriptions: dict[str, set[Channel]]

    def __init__(self, token: str, logger: Logger):
        Messenger.__init__(self, token)
        Runner.__init__(self, logger)
        self.subscriptions = Storage.import_subscriptions()
