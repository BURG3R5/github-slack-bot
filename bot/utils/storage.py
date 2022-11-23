"""
Contains the `Storage` class, to save and load subscriptions from a JSON file.
"""

import json
import os

from ..models.github import EventType, convert_keywords_to_events
from ..models.slack import Channel


class Storage:
    """
    A wrapper around two methods dealing with saving and loading subscriptions.
    """

    @staticmethod
    def export_subscriptions(subscriptions: dict[str, set[Channel]]):
        """
        Saves the passed subscriptions map in "data/subscriptions".
        :param subscriptions: Map containing the current subscriptions.
        """
        with open("data/subscriptions", mode="w", encoding="utf-8") as file:
            exportable_dict: dict[str, dict[str, list[str]]] = {
                repo: {
                    channel.name: [event.keyword for event in channel.events]
                    for channel in channels
                }
                for repo, channels in subscriptions.items()
            }
            print(f"EXPORTING:\n{exportable_dict}")
            json.dump(exportable_dict, file)

    @staticmethod
    def import_subscriptions() -> dict[str, set[Channel]]:
        """
        Loads subscriptions from "data/subscriptions", if it exists.
        If the file doesn't exist, returns default subscriptions for testing and dev.
        :return: Map containing the saved subscriptions.
        """
        if os.path.exists("data/subscriptions"):
            with open("data/subscriptions", encoding="utf-8") as file:
                imported_dict: dict[str, dict[str,
                                              list[str]]] = json.load(file)
                subscriptions: dict[str, set[Channel]] = {
                    repo: {
                        Channel(
                            name=channel,
                            events=convert_keywords_to_events(events),
                        )
                        for channel, events in channels.items()
                    }
                    for repo, channels in imported_dict.items()
                }
                return subscriptions
        else:
            # Default subscriptions, for dev and testing
            return {
                "github-slack-bot": {
                    Channel("#github-slack-bot", set(EventType)),
                }
            }
