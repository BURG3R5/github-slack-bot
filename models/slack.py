from typing import Optional

from models.github import EventType


class Channel:
    def __init__(self, name: str, events: list[EventType]):
        self.name = name
        self.events = events

    def is_subscribed_to(self, event: EventType) -> bool:
        return event in self.events


class Link:
    def __init__(self, url: Optional[str] = None, text: Optional[str] = None):
        self.url = url
        self.text = text

    def __str__(self) -> str:
        return f"<{self.url}|{self.text}>"
