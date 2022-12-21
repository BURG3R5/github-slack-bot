"""
Contains the `Runner` class, which reacts to slash commands.
"""
import hashlib
import hmac
import time
import urllib.parse
from typing import Any

from werkzeug.datastructures import Headers, ImmutableMultiDict

from ..models.github import EventType, convert_keywords_to_events
from ..utils.json import JSON
from ..utils.list_manip import intersperse
from ..utils.log import Logger
from .base import SlackBotBase


class Runner(SlackBotBase):
    """
    Reacts to received slash commands.
    """

    logger: Logger

    def __init__(
        self,
        logger: Logger,
        base_url: str,
        secret: str,
    ):
        SlackBotBase.__init__(self)
        self.logger = logger
        self.base_url = base_url
        self.secret = secret.encode("utf-8")

    def verify(
        self,
        body: bytes,
        headers: Headers,
    ) -> tuple[bool, str]:
        """
        Checks validity of incoming Slack request.

        :param body: Body of the HTTP request
        :param headers: Headers of the HTTP request

        :return: A tuple of the form (V, E) — where V indicates the validity, and E is the reason for the verdict.
        """

        if (("X-Slack-Signature" not in headers)
                or ("X-Slack-Request-Timestamp" not in headers)):
            return False, "Request headers are imperfect"

        timestamp = headers['X-Slack-Request-Timestamp']

        if abs(time.time() - int(timestamp)) > 60 * 5:
            return False, "Request is too old"

        expected_digest = headers["X-Slack-Signature"].split('=', 1)[-1]
        sig_basestring = ('v0:' + timestamp + ':').encode() + body
        digest = hmac.new(self.secret, sig_basestring,
                          hashlib.sha256).hexdigest()
        is_valid = hmac.compare_digest(expected_digest, digest)

        if not is_valid:
            return False, "Payload is imperfect"

        return True, "Request is secure and valid"

    def run(self, raw_json: ImmutableMultiDict) -> dict[str, Any] | None:
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
        if command == "/sel-subscribe" and len(args) > 0:
            current_unix_time = int(time.time() * 1000)
            self.logger.log_command(
                f"{current_unix_time}, {username}, "
                f"{current_channel}, subscribe, {', '.join(args)}")
            result = self.run_subscribe_command(
                current_channel=current_channel,
                args=args,
            )
        elif command == "/sel-unsubscribe" and len(args) > 0:
            current_unix_time = int(time.time() * 1000)
            self.logger.log_command(
                f"{current_unix_time}, {username}, "
                f"{current_channel}, unsubscribe, {', '.join(args)}")
            result = self.run_unsubscribe_command(
                current_channel=current_channel,
                args=args,
            )
        elif command == "/sel-list":
            result = self.run_list_command(
                current_channel=current_channel,
                ephemeral=(("quiet" in args) or ("q" in args)),
            )
        elif command == "/sel-help":
            result = self.run_help_command(args)

        return result

    def run_subscribe_command(
        self,
        current_channel: str,
        args: list[str],
    ) -> dict[str, Any]:
        """
        Triggered by "/sel-subscribe". Adds the passed events to the channel's subscriptions.

        :param current_channel: Name of the current channel.
        :param args: `list` of events to subscribe to.
        """

        repository = args[0]
        if repository.find('/') == -1:
            return self.send_wrong_syntax_message()

        new_events = convert_keywords_to_events(args[1:])

        subscriptions = self.storage.get_subscriptions(channel=current_channel,
                                                       repository=repository)
        if len(subscriptions) == 1:
            new_events |= subscriptions[0].events

        self.storage.update_subscription(
            channel=current_channel,
            repository=repository,
            events=new_events,
        )

        if len(subscriptions) == 0:
            return self.send_welcome_message(repository=repository)
        else:
            return self.run_list_command(current_channel, ephemeral=True)

    def send_welcome_message(self, repository: str) -> dict[str, Any]:
        """
        Sends a message to prompt authentication for creation of webhooks.

        :param repository: Repository for which webhook is to be created.
        """

        params = {"repository": repository}
        url = f"https://redirect.mdgspace.org/{self.base_url}" \
              f"/github/auth?{urllib.parse.urlencode(params)}"

        blocks = [{
            "type": "section",
            "text": {
                "type":
                "mrkdwn",
                "text":
                f"To subscribe to this repository, "
                f"please finish connecting your GitHub "
                f"account <{url}|here>"
            }
        }]
        return {
            "response_type": "ephemeral",
            "blocks": blocks,
        }

    def run_unsubscribe_command(
        self,
        current_channel: str,
        args: list[str],
    ) -> dict[str, Any]:
        """
        Triggered by "/sel-unsubscribe". Removes the passed events from the channel's subscriptions.

        :param current_channel: Name of the current channel.
        :param args: `list` of events to unsubscribe from.
        """

        repository = args[0]
        if repository.find('/') == -1:
            return self.send_wrong_syntax_message()

        subscriptions = self.storage.get_subscriptions(
            channel=current_channel,
            repository=repository,
        )

        if len(subscriptions) == 0:
            return {
                "response_type":
                "ephemeral",
                "blocks": [{
                    "type": "section",
                    "text": {
                        "type":
                        "mrkdwn",
                        "text":
                        f"Found no subscriptions to `{repository}` in this channel"
                    }
                }]
            }

        if len(subscriptions) == 1:
            events = subscriptions[0].events
            updated_events = set(events) - convert_keywords_to_events(
                (args[1:]))

            if len(updated_events) == 0:
                self.storage.remove_subscription(channel=current_channel,
                                                 repository=repository)
            else:
                self.storage.update_subscription(channel=current_channel,
                                                 repository=repository,
                                                 events=updated_events)

        return self.run_list_command(current_channel, ephemeral=True)

    @staticmethod
    def send_wrong_syntax_message() -> dict[str, Any]:
        blocks = [
            {
                "text": {
                    "type":
                    "mrkdwn",
                    "text":
                    ("*Invalid syntax for repository name!*\nPlease include owner/organisation name in repository name.\n_For example:_ `BURG3R5/github-slack-bot`"
                     ),
                },
                "type": "section",
            },
        ]
        return {
            "response_type": "ephemeral",
            "blocks": blocks,
        }

    def run_list_command(
        self,
        current_channel: str,
        ephemeral: bool = False,
    ) -> dict[str, Any]:
        """
        Triggered by "/sel-list". Sends a message listing the current channel's subscriptions.

        :param current_channel: Name of the current channel.
        :param ephemeral: Whether message should be ephemeral or not.

        :return: Message containing subscriptions for the passed channel.
        """

        blocks: list[dict[str, Any]] = []
        subscriptions = self.storage.get_subscriptions(channel=current_channel)
        for subscription in subscriptions:
            events_string = ", ".join(f"`{event.name.lower()}`"
                                      for event in subscription.events)
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{subscription.repository}*\n{events_string}",
                },
            })
        if len(blocks) != 0:
            blocks = intersperse(blocks, {"type": "divider"})
        else:
            ephemeral = True
            blocks = [
                {
                    "text": {
                        "type":
                        "mrkdwn",
                        "text":
                        ("This channel has not yet subscribed to anything. "
                         "You can subscribe to your favorite repositories "
                         "using the `/sel-subscribe` command. For more info, "
                         "use the `/sel-help` command."),
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
        Triggered by "/sel-help". Sends an ephemeral help message as response.

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
                    "*/sel-unsubscribe*\n"
                    "Unsubscribe from events in a GitHub repository\n\n"
                    "Format: `/sel-unsubscribe <owner>/<repository> <event1> [<event2> <event3> ...]`"
                )
            elif "subscribe" in query:
                return mini_help_response(
                    "*/sel-subscribe*\n"
                    "Subscribe to events in a GitHub repository\n\n"
                    "Format: `/sel-subscribe <owner>/<repository> <event1> [<event2> <event3> ...]`"
                )
            elif "list" in query:
                return mini_help_response(
                    "*/sel-list*\n"
                    "Lists subscriptions for the current channel\n\n"
                    "Format: `/sel-list ['q' or 'quiet']`")
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
                         "1. `/sel-subscribe <owner>/<repository> <event1> [<event2> <event3> ...]`\n"
                         "2. `/sel-unsubscribe <owner>/<repository> <event1> [<event2> <event3> ...]`\n"
                         "3. `/sel-list ['q' or 'quiet']`\n"
                         "4. `/sel-help [<event name or keyword or command>]`"
                         ),
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
