from typing import Any

from bot.models.github.event import GitHubEvent


def github_event_serializer(github_event: GitHubEvent) -> dict[str, Any]:
    serialized = {}
    for var, value in vars(github_event).items():
        if isinstance(value, (list, tuple, set)):
            serialized[var] = [str(v) for v in value]
        else:
            serialized[var] = str(value)
    return serialized
