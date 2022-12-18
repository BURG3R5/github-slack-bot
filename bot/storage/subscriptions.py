"""
Contains the `SubscriptionStorage` class, to save and fetch subscriptions using the peewee library.
"""
from typing import Optional

from peewee import CharField, Model, SqliteDatabase
from playhouse.fields import PickleField

from bot.models.github import EventType, convert_keywords_to_events

db = SqliteDatabase(None)


class SubscriptionStorage:
    """
    Uses the `peewee` library to save and fetch subscriptions from an SQL database.
    """

    def __init__(self):
        global db
        db.init("data/subscriptions.db")
        db.connect()
        Subscription.create_table()
        Subscription.insert(
            channel="#selene",
            repository="BURG3R5/github-slack-bot",
            events=list(EventType),
        )

    def remove_subscription(self, channel: str, repository: str):
        """
        Deletes a given entry from the database.

        :param channel: Name of the Slack channel (including the "#")
        :param repository: Unique identifier of the GitHub repository, of the form "<owner-name>/<repo-name>"
        """

        Subscription\
            .delete()\
            .where((Subscription.channel == channel) & (Subscription.repository == repository))\
            .execute()

    def update_subscription(
        self,
        channel: str,
        repository: str,
        events: set[EventType],
    ):
        """
        Creates or updates subscription object in the database.

        :param channel: Name of the Slack channel (including the "#")
        :param repository: Unique identifier of the GitHub repository, of the form "<owner-name>/<repo-name>"
        :param events: Set of events to subscribe to
        """

        Subscription.insert(
            channel=channel,
            repository=repository,
            events=[e.keyword for e in events],
        ).on_conflict_replace().execute()

    def get_subscriptions(
        self,
        channel: Optional[str] = None,
        repository: Optional[str] = None,
    ) -> tuple["Subscription"]:
        """
        Queries the subscriptions database. Filters are applied depending on arguments passed.

        :param channel: Name of the Slack channel (including the "#")
        :param repository: Unique identifier for the GitHub repository, of the form "<owner-name>/<repo-name>"

        :return: Result of query, containing `Subscription` objects with relevant fields
        """

        if channel is None and repository is None:
            # No filters are provided
            subscriptions = Subscription.select()
        elif channel is None:
            # Only repository filter is provided
            subscriptions = Subscription\
                .select(Subscription.channel, Subscription.events)\
                .where(Subscription.repository == repository)
        elif repository is None:
            # Only channel filter is provided
            subscriptions = Subscription\
                .select(Subscription.repository, Subscription.events)\
                .where(Subscription.channel == channel)
        else:
            # Both filters are provided
            subscriptions = Subscription\
                .select(Subscription.events)\
                .where((Subscription.channel == channel) & (Subscription.repository == repository))

        return tuple(
            Subscription(
                channel=subscription.channel,
                repository=subscription.repository,
                events=convert_keywords_to_events(subscription.events),
            ) for subscription in subscriptions)


class Subscription(Model):
    """
    A peewee-friendly model that represents one subscription.

    :keyword channel: Name of the Slack channel, including the "#"
    :keyword repository: Unique identifier for the GitHub repository, of the form "<owner-name>/<repo-name>"
    :keyword events: List of keyword-representations of EventType enum members
    """

    channel = CharField()
    repository = CharField()
    #        v A field that stores any Python object in a pickled string and un-pickles it automatically.
    events = PickleField()

    class Meta:
        database = db
        indexes = ((("channel", "repository"), True), )
        # ^ Each (channel, repository) pair should be unique together

    def __str__(self):
        return f"({self.channel},{self.repository}) — {self.events}"
