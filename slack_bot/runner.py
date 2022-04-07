"""
Contains the `Runner` class, which reacts to slash commands.
"""

from typing import Any

from bottle import MultiDict

from models.github import EventType, convert_str_to_event_type
from models.slack import Channel
from utils.json import JSON
from utils.storage import Storage


class Runner:
    """
    Reacts to received slash commands.
    """

    def __init__(self):
        # Dummy initialization. Overridden in `SlackBot.__init__()`.
        self.subscriptions: dict[str, set[Channel]] = {}

    def run(self, raw_json: MultiDict) -> dict[str, Any] | None:
        """
        Runs Slack slash commands sent to the bot.
        :param raw_json: Slash command data sent by Slack.
        :return: Response to the triggered command, in Slack block format.
        """
        json: JSON = JSON.from_multi_dict(raw_json)
        current_channel: str = "#" + json["channel_name"]
        command: str = json["command"]
        args: list[str] = str(json["text"]).split()
        if command == "/subscribe" and len(args) > 0:
            self.run_subscribe_command(current_channel=current_channel, args=args)
        elif command == "/unsubscribe" and len(args) > 0:
            self.run_unsubscribe_command(current_channel=current_channel, args=args)
        elif command == "/list":
            return self.run_list_command(current_channel=current_channel)
        elif command == "/help":
            return self.run_help_command()
        Storage.export_subscriptions(self.subscriptions)
        return None

    def run_subscribe_command(self, current_channel: str, args: list[str]) -> None:
        """
        Triggered by "/subscribe". Adds the passed events to the channel's subscriptions.
        :param current_channel: Name of the current channel.
        :param args: `list` of events to subscribe to.
        """
        repo: str = args[0]
        new_events: set[EventType] = {
            convert_str_to_event_type(arg) for arg in args[1:]
        }
        # Remove all the entries which do not correspond to a correct [EventType].
        new_events -= [None]
        if repo in self.subscriptions:
            channels: set[Channel] = self.subscriptions[repo]
            channel: Channel | None = next(
                (
                    subscribed_channel
                    for subscribed_channel in channels
                    if subscribed_channel.name == current_channel
                ),
                None,
            )
            if channel is None:
                # If this channel has not subscribed to any events
                # from this repo, add a subscription.
                channels.add(
                    Channel(
                        name=current_channel,
                        events=new_events,
                    )
                )
                self.subscriptions[repo] = channels
            else:
                # If this channel has subscribed to some events
                # from this repo, update the list of events.
                old_events: set[EventType] = channel.events
                self.subscriptions[repo].remove(channel)
                self.subscriptions[repo].add(
                    Channel(
                        name=current_channel,
                        events=(old_events.union(new_events)),
                    )
                )
        else:
            # If no one has subscribed to this repo, add a repo entry.
            self.subscriptions[repo] = {
                Channel(
                    name=current_channel,
                    events=new_events,
                )
            }

    def run_unsubscribe_command(self, current_channel: str, args: list[str]) -> None:
        """
        Triggered by "/unsubscribe". Removes the passed events from the channel's subscriptions.
        :param current_channel: Name of the current channel.
        :param args: `list` of events to unsubscribe from.
        """
        repo: str = args[0]
        channels: set[Channel] = self.subscriptions[repo]
        channel: Channel | None = next(
            (
                subscribed_channel
                for subscribed_channel in channels
                if subscribed_channel.name == current_channel
            ),
            None,
        )
        if channel is not None:
            # If this channel has subscribed to some events
            # from this repo, update the list of events.
            events = channel.events
            for arg in args[1:]:
                event: EventType | None = convert_str_to_event_type(arg)
                try:
                    events.remove(event)
                except KeyError:
                    # This means that the user tried to unsubscribe from
                    # an event that wasn't subscribed to in the first place.
                    pass
            self.subscriptions[repo].remove(channel)
            if len(events) != 0:
                self.subscriptions[repo].add(
                    Channel(
                        name=current_channel,
                        events=events,
                    )
                )

    def run_list_command(self, current_channel: str) -> dict[str, Any]:
        """
        Triggered by "/list". Sends a message listing the current channel's subscriptions.
        :param current_channel: Name of the current channel.
        :return: Message containing subscriptions for the passed channel.
        """
        blocks: list[dict] = []
        for repo, channels in self.subscriptions.items():
            channel: Channel | None = next(
                (
                    subscribed_channel
                    for subscribed_channel in channels
                    if subscribed_channel.name == current_channel
                ),
                None,
            )
            if channel is None:
                continue
            events_string = ", ".join(event.keyword for event in channel.events)
            blocks += [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{repo}*\n{events_string}",
                    },
                },
                {
                    "type": "divider",
                },
            ]
        return {
            "response_type": "in_channel",
            "blocks": blocks,
        }

    @staticmethod
    def run_help_command() -> dict[str, Any]:
        """
        Triggered by "/help". Sends an ephemeral help message as response.
        :return: Ephemeral message showcasing the bot features and keywords.
        """
        # TODO: Prettify events section.
        return {
            "response_type": "ephemeral",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            "*Commands*\n"
                            "1. `/subscribe <repo> <event1> [<event2> ...]`\n"
                            "2. `/unsubsribe <repo> <event1> [<event2> ...]`\n"
                            "3. `/list`\n"
                            "4. `/help`"
                        ),
                    },
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            "*Events*\n"
                            "GitHub events are abbreviated as follows:\n"
                            + " ".join(
                                [
                                    f"{i + 1}. `{event.keyword}`: {event.docs}\n"
                                    for i, event in enumerate(EventType)
                                ]
                            )
                        ),
                    },
                },
            ],
        }
