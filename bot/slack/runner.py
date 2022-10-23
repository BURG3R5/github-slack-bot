"""
Contains the `Runner` class, which reacts to slash commands.
"""

import time
from typing import Any

import slack
from bottle import MultiDict

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

    def __init__(self, logger: Logger):
        self.logger = logger
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
            result = self.run_help_command()
        elif command == "/gh-cls":
            result = self.run_cls_command(number_of_message=args)

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
            prompt = "This channel has not yet subscribed to anything."
            prompt += "You can subscribe to your favorite repositories "
            prompt += "using the `/subscribe` command. For more info, use the `/help` command."

            blocks = [
                {
                    "type": "mrkdwn",
                    "text": prompt,
                },
            ]
        return {
            "response_type": "ephemeral" if ephemeral else "in_channel",
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
                         "1. `/subscribe <repo> <event1> [<event2> ...]`\n"
                         "2. `/unsubsribe <repo> <event1> [<event2> ...]`\n"
                         "3. `/list`\n"
                         "4. `/help`"),
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
                         "0. `default` or no arguments: Subscribe "
                         "to the most common and important events.\n"
                         "1. `all` or `*`: Subscribe to every supported event.\n"
                         + " ".join([
                             f"{i + 2}. `{event.keyword}`: {event.docs}\n"
                             for i, event in enumerate(EventType)
                         ])),
                    },
                },
            ],
        }

    def run_cls_command(self, args: list[int]):
        num = 0
        if args[1] is None:
            if args[0] < 1000:
                if args[0] is not None:
                    num = args[0]
                conversattion_history = []
                channel_id = "C03PET0R015"
                try:
                    client = slack.Webclient(token="token")
                    result = client.conversations_history(channel=channel_id,
                                                          limit=num)

                    conversation_history = result["messages"]
                    ephemral_history = result

                    for i in range(0, num):
                        if (conversation_history[i][type] == "ephemeral"):
                            ts = conversation_history[i][ts]
                            try:
                                delete_msg = client.chat_delete(
                                    channel=channel_id, ts=ts)
                            except:
                                print("error")
                except:
                    print("Error creating conversation")
            elif args[1] > 1000:
                return {
                    "response_type":
                    "ephemeral",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "Can only delete 1000 msg at once!",
                            },
                        },
                    ]
                }
        else:
            return {
                "response_type":
                "ephemeral",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Only 1 argument is allowed at a time!",
                        },
                    },
                ]
            }
