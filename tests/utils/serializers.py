from typing import Any

from bot.models.github.event import GitHubEvent


def github_event_serializer(github_event: GitHubEvent) -> dict[str, Any]:
    serialized = {}
    for var, value in vars(github_event).items():
        serialized[var] = str(value)
    return serialized
