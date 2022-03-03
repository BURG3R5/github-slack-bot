"""
Contains the `Storage` class, to save and load subscriptions from a JSON file.
"""

import json
import os

from models.github import EventType, convert_str_to_event_type
from models.slack import Channel


class Storage:
    """
    A wrapper around two methods dealing with saving and loading subscriptions.
    """

    @staticmethod
    def export_subscriptions(subscriptions: dict[str, set[Channel]]) -> None:
        """
        Saves the passed subscriptions map to the file ".data".
        :param subscriptions: Map containing the current subscriptions.
        """
        with open(".data", mode="w", encoding="utf-8") as file:
            exportable_dict: dict[str, dict[str, list[str]]] = {
                repo: {
                    channel.name: [event.value for event in channel.events]
                    for channel in channels
                }
                for repo, channels in subscriptions.items()
            }
            print(f"EXPORTING:\n{exportable_dict}")
            json.dump(exportable_dict, file)

    @staticmethod
    def import_subscriptions() -> dict[str, set[Channel]]:
        """
        Loads subscriptions from the file ".data", if it exists.
        If there is no ".data" file, returns default subscriptions for testing and dev.
        :return: Map containing the saved subscriptions.
        """
        if os.path.exists(".data"):
            with open(".data", encoding="utf-8") as file:
                imported_dict: dict[str, dict[str, list[str]]] = json.load(file)
                subscriptions: dict[str, set[Channel]] = {
                    repo: {
                        Channel(
                            name=channel,
                            events={
                                convert_str_to_event_type(event_keyword)
                                for event_keyword in events
                            },
                        )
                        for channel, events in channels.items()
                    }
                    for repo, channels in imported_dict.items()
                }
                return subscriptions
        else:
            # Default subscriptions, for dev and testing
            return {
                "fake-rdrive-flutter": {
                    Channel("#github-slack-bot", set(EventType)),
                }
            }
