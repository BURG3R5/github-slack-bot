"""
Collection of models related to the Slack portion of the project.
"""

from .github import EventType


class Channel:
    """
    Model for a Slack channel with event subscriptions.

    :param name: The channel name, including the "#".
    :param events: `set` of events the channel has subscribed to.
    """

    def __init__(self, name: str, events: set[EventType]):
        self.name = name
        self.events = events

    def is_subscribed_to(self, event: EventType) -> bool:
        """
        Wrapper for `__contains__` to make the use and result more evident.
        :param event: EventType to be checked.
        :return: Whether the channel is subscribed to the passed event or not.
        """
        return event in self.events

    def __str__(self) -> str:
        return self.name
