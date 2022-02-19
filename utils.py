import json
from os.path import exists
from typing import Any

from bottle import MultiDict

from models.github import EventType
from models.slack import Channel


class JSON:
    """Wrapper for a `dict`.
    Safely extracts values using multiple keys."""

    def __contains__(self, key) -> bool:
        return key in self.data

    def __init__(self, dictionary) -> None:
        self.data = dictionary

    def __getitem__(self, keys) -> Any:
        def get(k):
            if isinstance(self.data[k], dict):
                return JSON(self.data[k])
            return self.data[k]

        # Single key
        if isinstance(keys, str):
            key = keys
            if key in self.data:
                return get(key)
            return key.upper()
        # Multiple keys
        for key in keys:
            if key in self.data:
                return get(key)
        return keys[0].upper()

    @staticmethod
    def from_multi_dict(multi_dict: MultiDict):
        return JSON({key: multi_dict[key] for key in multi_dict.keys()})


class StorageUtils:
    @staticmethod
    def export_subscriptions(subscriptions: dict[str, set[Channel]]) -> None:
        with open(".data", mode="w", encoding="utf-8") as file:
            exportable_dict: dict[str, dict[str, list[str]]] = {
                repo: {
                    channel.name: [event.value for event in channel.events]
                    for channel in channels
                }
                for repo, channels in subscriptions.items()
            }
            print(f"EXPORTING: {exportable_dict}")
            json.dump(exportable_dict, file)

    @staticmethod
    def import_subscriptions() -> dict[str, set[Channel]]:
        if exists(".data"):
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


def convert_str_to_event_type(event_keyword: str) -> EventType | None:
    for event_type in EventType:
        if event_type.value == event_keyword:
            return event_type
    print("Event not in enum")
    return None
