from typing import NamedTuple, Optional

from bot.models.github import EventType


class Subscription(NamedTuple):
    channel: str
    repository: str
    events: set[EventType]


class MockSubscriptionStorage:

    def __init__(self, subscriptions: list[Subscription] = None):
        if subscriptions is None:
            self.subscriptions = [
                Subscription(
                    "workspace#selene",
                    "BURG3R5/github-slack-bot",
                    set(EventType),
                )
            ]
        else:
            self.subscriptions = subscriptions

    def get_subscriptions(
        self,
        channel: Optional[str] = None,
        repository: Optional[str] = None,
    ) -> tuple[Subscription, ...]:
        shortlist = self.subscriptions
        if channel is not None:
            shortlist = (sub for sub in self.subscriptions
                         if sub.channel == channel)
        if repository is not None:
            shortlist = (sub for sub in self.subscriptions
                         if sub.repository == repository)
        return tuple(shortlist)
