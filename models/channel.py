class Channel:
    def __init__(self, name: str, events: list[str]):
        self.name = name
        self.events = events

    def is_subscribed_to(self, event: str) -> bool:
        return event in self.events
