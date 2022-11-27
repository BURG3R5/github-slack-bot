"""
Contains the `Runner` class, which reacts to slash commands.
"""
import time
from typing import Any

from bottle import MultiDict
from sentry_sdk import capture_message
from slack.errors import SlackApiError
from slack.web.client import WebClient

from ..models.github import EventType, convert_keywords_to_events
from ..models.slack import Channel
from ..utils.json import JSON
from ..utils.log import Logger
from ..utils.storage import Storage


class Runner:
    """
    Reacts to received slash commands.
    """

    logger: Logger

    def __init__(self, token: str, logger: Logger, bot_id: str):
        self.logger = logger
        self.client = WebClient(token)
        self.bot_id = bot_id

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
        username: str = json["user_name"]
        command: str = json["command"]
        args: list[str] = str(json["text"]).split()
        result: dict[str, Any] | None = None
        if command == "/subscribe" and len(args) > 0:
            current_unix_time = int(time.time() * 1000)
            self.logger.log_command(
                f"{current_unix_time}, {username}, "
                f"{current_channel}, subscribe, {', '.join(args)}")
            result = self.run_subscribe_command(
                current_channel=current_channel,
                args=args,
            )
        elif command == "/unsubscribe" and len(args) > 0:
            current_unix_time = int(time.time() * 1000)
            self.logger.log_command(
                f"{current_unix_time}, {username}, "
                f"{current_channel}, unsubscribe, {', '.join(args)}")
            result = self.run_unsubscribe_command(
                current_channel=current_channel,
                args=args,
            )
        elif command == "/list":
            result = self.run_list_command(current_channel=current_channel)
        elif command == "/help":
            result = self.run_help_command(args)
        elif command == "/gh-cls":
            result = self.run_cls_command(current_channel=json["channel_id"])

        Storage.export_subscriptions(self.subscriptions)
        return result

    def run_subscribe_command(
        self,
        current_channel: str,
        args: list[str],
    ) -> dict[str, Any]:
        """
        Triggered by "/subscribe". Adds the passed events to the channel's subscriptions.
        :param current_channel: Name of the current channel.
        :param args: `list` of events to subscribe to.
        """
        repo: str = args[0]
        new_events = convert_keywords_to_events(args[1:])
        if repo in self.subscriptions:
            channels: set[Channel] = self.subscriptions[repo]
            channel: Channel | None = next(
                (subscribed_channel for subscribed_channel in channels
                 if subscribed_channel.name == current_channel),
                None,
            )
            if channel is None:
                # If this channel has not subscribed to any events
                # from this repo, add a subscription.
                channels.add(Channel(
                    name=current_channel,
                    events=new_events,
                ))
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
                    ))
        else:
            # If no one has subscribed to this repo, add a repo entry.
            self.subscriptions[repo] = {
                Channel(
                    name=current_channel,
                    events=new_events,
                )
            }
        return self.run_list_command(current_channel, True)

    def run_unsubscribe_command(
        self,
        current_channel: str,
        args: list[str],
    ) -> dict[str, Any]:
        """
        Triggered by "/unsubscribe". Removes the passed events from the channel's subscriptions.
        :param current_channel: Name of the current channel.
        :param args: `list` of events to unsubscribe from.
        """
        repo: str = args[0]
        channels: set[Channel] = self.subscriptions[repo]
        channel: Channel | None = next(
            (subscribed_channel for subscribed_channel in channels
             if subscribed_channel.name == current_channel),
            None,
        )
        if channel is not None:
            # If this channel has subscribed to some events
            # from this repo, update the list of events.
            current_events = channel.events
            chosen_events = convert_keywords_to_events(args[1:])
            for event in chosen_events:
                try:
                    current_events.remove(event)
                except KeyError:
                    # This means that the user tried to unsubscribe from
                    # an event that wasn't subscribed to in the first place.
                    pass
            self.subscriptions[repo].remove(channel)
            if len(current_events) != 0:
                self.subscriptions[repo].add(
                    Channel(
                        name=current_channel,
                        events=current_events,
                    ))
        return self.run_list_command(current_channel, True)

    def run_list_command(
        self,
        current_channel: str,
        ephemeral: bool = False,
    ) -> dict[str, Any]:
        """
        Triggered by "/list". Sends a message listing the current channel's subscriptions.
        :param current_channel: Name of the current channel.
        :param ephemeral: Whether message should be ephemeral or not.
        :return: Message containing subscriptions for the passed channel.
        """
        blocks: list[dict] = []
        for repo, channels in self.subscriptions.items():
            channel: Channel | None = next(
                (subscribed_channel for subscribed_channel in channels
                 if subscribed_channel.name == current_channel),
                None,
            )
            if channel is None:
                continue
            events_string = ", ".join(f"`{event.name.lower()}`"
                                      for event in channel.events)
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
        if len(blocks) == 0:
            blocks = [
                {
                    "text": {
                        "type":
                        "mrkdwn",
                        "text":
                        ("This channel has not yet subscribed to anything. "
                         "You can subscribe to your favorite repositories "
                         "using the `/subscribe` command. For more info, "
                         "use the `/help` command."),
                    },
                    "type": "section",
                },
            ]
        return {
            "response_type": "ephemeral" if ephemeral else "in_channel",
            "blocks": blocks,
        }

    @staticmethod
    def run_help_command(args: list[str]) -> dict[str, Any]:
        """
        Triggered by "/help". Sends an ephemeral help message as response.

        :param args: Arguments passed to the command.

        :return: Ephemeral message showcasing the bot features and keywords.
        """

        def mini_help_response(text: str) -> dict[str, Any]:
            return {
                "response_type":
                "ephemeral",
                "blocks": [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text
                    }
                }],
            }

        if len(args) == 1:
            query = args[0].lower()
            if "unsubscribe" in query:
                return mini_help_response(
                    "*/unsubscribe*\n"
                    "Unsubscribe from events in a GitHub repository\n\n"
                    "Format: `/unsubscribe <owner>/<repository> <event1> [<event2> <event3> ...]`"
                )
            elif "subscribe" in query:
                return mini_help_response(
                    "*/subscribe*\n"
                    "Subscribe to events in a GitHub repository\n\n"
                    "Format: `/subscribe <owner>/<repository> <event1> [<event2> <event3> ...]`"
                )
            elif "list" in query:
                return mini_help_response(
                    "*/list*\n"
                    "Lists subscriptions for the current channel\n\n"
                    "Format: `/list`")
            else:
                for event in EventType:
                    if ((query == event.keyword)
                            or (query == event.name.lower())):
                        return mini_help_response(f"`{event.keyword}`: "
                                                  f"{event.docs}")
        return {
            "response_type":
            "ephemeral",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type":
                        "mrkdwn",
                        "text":
                        ("*Commands*\n"
                         "1. `/subscribe <owner>/<repository> <event1> [<event2> <event3> ...]`\n"
                         "2. `/unsubscribe <owner>/<repository> <event1> [<event2> <event3> ...]`\n"
                         "3. `/list`\n"
                         "4. `/help [<event name or keyword or command>]`"),
                    },
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type":
                        "mrkdwn",
                        "text":
                        ("*Events*\n"
                         "GitHub events are abbreviated as follows:\n"
                         "- `default` or no arguments: Subscribe "
                         "to the most common and important events.\n"
                         "- `all` or `*`: Subscribe to every supported event.\n"
                         + "".join([
                             f"- `{event.keyword}`: {event.docs}\n"
                             for event in EventType
                         ])),
                    },
                },
            ],
        }

    def run_cls_command(self, current_channel: str):

        def error_response(error: str):
            return {
                "response_type":
                "ephemeral",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": error,
                        },
                    },
                ]
            }

        # Get number_of_messages_to_scan
        try:
            history = self.client.conversations_history(
                channel=current_channel,
                limit=100,
            )["messages"]

            for message in history:
                if (message["type"] == "message" and "subtype" in message
                        and message["subtype"] == "bot_message"
                        and message["bot_id"] == self.bot_id):
                    timestamp = message["ts"]
                    try:
                        print(current_channel)
                        self.client.chat_delete(
                            channel=current_channel,
                            ts=timestamp,
                        )
                    except SlackApiError as E:
                        capture_message(
                            f"SlackApiError {E} Failed to delete message '{message['blocks']}'"
                        )
                        return error_response(
                            f"Failed to delete message with timestamp {timestamp}"
                        )
        except SlackApiError as E:
            capture_message(
                f"SlackApiError {E} Failed to fetch conversation history for #{current_channel}"
            )
            return error_response(
                "Error fetching conversation history. "
                "Please provide proper permissions to the bot.")

        return {
            "response_type":
            "in_channel",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Cleared bot messages from last 100 messages",
                    },
                },
            ]
        }
