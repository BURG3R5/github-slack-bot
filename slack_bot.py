"""
Contains the `SlackBot` class, to handle all Slack-related features.

Important methods—
* `SlackBot.inform` to notify channels about events,
* `SlackBot.run` to execute slash commands.
"""

import os
from pathlib import Path
from typing import Any

from bottle import MultiDict
from dotenv import load_dotenv
from slack.web.client import WebClient  # pylint: disable=no-name-in-module

from models.slack import Channel
from models.github import GitHubEvent, EventType
from utils import JSON, convert_str_to_event_type, StorageUtils


class SlackBot:
    """
    Class providing access to all functions required by the Slack portion of the project.
    """

    def __init__(self):
        load_dotenv(Path(".") / ".env")
        self.client: WebClient = WebClient(os.environ["SLACK_OAUTH_TOKEN"])
        self.subscriptions: dict[
            str, set[Channel]
        ] = StorageUtils.import_subscriptions()

    # Messaging related methods
    def inform(self, event: GitHubEvent) -> None:
        """
        Notify the subscribed channels about the passed event.
        :param event: `GitHubEvent` containing all relevant data about the event.
        """
        message, details = SlackBot.compose_message(event)
        correct_channels: list[str] = self.calculate_channels(
            repo=event.repo.name,
            event_type=event.type,
        )
        for channel in correct_channels:
            self.send_message(channel=channel, message=message, details=details)

    def calculate_channels(self, repo: str, event_type: EventType) -> list[str]:
        """
        Determines the Slack channels that need to be notified about the passed event.
        :param repo: Name of the repository that the event was triggered in.
        :param event_type: Enum-ized type of event.
        :return: `list` of names of channels that are subscribed to the repo+event_type.
        """
        if repo not in self.subscriptions:
            return []
        correct_channels: list[str] = [
            channel.name
            for channel in self.subscriptions[repo]
            if channel.is_subscribed_to(event=event_type)
        ]
        return correct_channels

    # pylint: disable=too-many-branches
    @staticmethod
    def compose_message(event: GitHubEvent) -> tuple[str, str | None]:
        """
        Create message and details strings according to the type of event triggered.
        :param event: `GitHubEvent` containing all relevant data about the event.
        :return: `tuple` containing the main message and optionally, extra details.
        """
        message: str = ""
        details: str | None = None

        # TODO: Beautify messages.
        if event.type == EventType.BRANCH_CREATED:
            message = f"Branch created by {event.user}: `{event.ref}`"
        elif event.type == EventType.BRANCH_DELETED:
            message = f"Branch deleted by {event.user}: `{event.ref}`"
        elif event.type == EventType.COMMIT_COMMENT:
            message = (
                f"<{event.links[0].url}|Comment on `{event.commits[0].sha}`> "
                f"by {event.user}\n>{event.comments[0]}"
            )
        elif event.type == EventType.FORK:
            message = f"<{event.links[0].url}|Repository forked> by {event.user}"
        elif event.type == EventType.ISSUE_OPENED:
            message = f"Issue opened by {event.user}:\n>{event.issue}"
        elif event.type == EventType.ISSUE_CLOSED:
            message = f"Issue closed by {event.user}:\n>{event.issue}"
        elif event.type == EventType.ISSUE_COMMENT:
            type_of_discussion = "Issue" if "issue" in event.issue.link else "PR"
            message = (
                f"<{event.links[0].url}|Comment on {type_of_discussion} #{event.issue.number}> "
                f"by {event.user}\n>{event.comments[0]}"
            )
        elif event.type == EventType.PULL_CLOSED:
            message = f"PR closed by {event.user}:\n>{event.pull_request}"
        elif event.type == EventType.PULL_MERGED:
            message = f"PR merged by {event.user}:\n>{event.pull_request}"
        elif event.type == EventType.PULL_OPENED:
            message = f"PR opened by {event.user}:\n>{event.pull_request}"
        elif event.type == EventType.PULL_READY:
            message = (
                f"Review requested on {event.pull_request}\n"
                f">Reviewers: {', '.join(str(reviewer) for reviewer in event.reviewers)}"
            )
        elif event.type == EventType.PUSH:
            message = f"{event.user} pushed to `{event.ref}`, "
            if len(event.commits) == 1:
                message += "1 new commit."
            else:
                message += f"{len(event.commits)} new commits."
            details = "\n".join(
                f"`{commit.sha}` - {commit.message}" for commit in event.commits
            )
        elif event.type == EventType.RELEASE:
            message = f"Release {event.status} by {event.user}: `{event.ref}`"
        elif event.type == EventType.REVIEW:
            message = (
                f"Review on <{event.pull_request.link}|#{event.pull_request.number}> "
                f"by {event.reviewers[0]}:\n>Status: "
                f"{'Approved' if event.status == 'approved' else 'Changed requested'}"
            )
        elif event.type == EventType.REVIEW_COMMENT:
            message = (
                f"<{event.links[0].url}|Comment on PR #{event.pull_request.number}> "
                f"by {event.user}\n>{event.comments[0]}"
            )
        elif event.type == EventType.STAR_ADDED:
            message = f"`{event.repo.name}` received a star."
        elif event.type == EventType.STAR_REMOVED:
            message = f"`{event.repo.name}` lost a star."
        elif event.type == EventType.TAG_CREATED:
            message = f"Tag created by {event.user}: `{event.ref}`"
        elif event.type == EventType.TAG_DELETED:
            message = f"Tag deleted by {event.user}: `{event.ref}`"

        return message, details

    def send_message(self, channel: str, message: str, details: str | None) -> None:
        """
        Sends the passed message to the passed channel.
        Also, optionally posts `details` in a thread under the main message.
        :param channel: Channel to send the message to.
        :param message: Main message, briefly summarizing the event.
        :param details: Text to be sent as a reply to the main message. Verbose stuff goes here.
        """
        print(f"\n\nSENDING:\n{message}\n\nWITH DETAILS:\n{details}\n\nTO: {channel}")
        if details is None:
            self.client.chat_postMessage(
                channel=channel,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message,
                        },
                    }
                ],
                unfurl_links=False,
            )
        else:
            response = self.client.chat_postMessage(
                channel=channel,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message,
                        },
                    }
                ],
                unfurl_links=False,
            )
            message_id = response.data["ts"]
            self.client.chat_postMessage(
                channel=channel,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": details,
                        },
                    }
                ],
                thread_ts=message_id,
                unfurl_links=False,
            )

    # Slash commands related methods
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
        StorageUtils.export_subscriptions(self.subscriptions)
        return None

    def run_subscribe_command(self, current_channel: str, args: list[str]) -> None:
        """
        Triggered by "/subscribe". Adds the passed events to the channel's subscriptions.
        :param current_channel: Name of the current channel.
        :param args: `list` of events to subscribe to.
        """
        repo: [str] = args[0]
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
        repo: [str] = args[0]
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
