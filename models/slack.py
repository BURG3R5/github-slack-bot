from models.github import EventType


class Channel:
    def __init__(self, name: str, events: set[EventType]):
        self.name = name
        self.events = events

    def is_subscribed_to(self, event: EventType) -> bool:
        return event in self.events
