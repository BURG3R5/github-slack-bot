from typing import Any

from bot.models.github import convert_keywords_to_events
from bot.models.slack import Channel


def github_payload_deserializer(json: dict[str, Any]):
    return json["event_type"], json["raw_json"]


def subscriptions_deserializer(json: dict[str, dict[str, list[str]]]):
    return {
        repo: {
            Channel(
                name=channel,
                events=convert_keywords_to_events(events),
            )
            for channel, events in channels.items()
        }
        for repo, channels in json.items()
    }
