import os
from pathlib import Path
from typing import Optional

from bottle import MultiDict
from dotenv import load_dotenv
from slack import WebClient

from models.slack import Channel
from models.github import GitHubEvent, EventType
from utils import JSON


class SlackBot:
    def __init__(self):
        load_dotenv(Path(".") / ".env")
        self.client = WebClient(os.environ["SLACK_OAUTH_TOKEN"])
        self.subscriptions: dict[str, set[Channel]] = {
            "fake-rdrive-flutter": {
                Channel(
                    "#github-slack-bot",
                    {
                        EventType.branch_created,
                        EventType.push,
                        EventType.pull_opened,
                    },
                ),
            }
        }

    # Messaging related methods
    def inform(self, event: GitHubEvent) -> None:
        message, details = SlackBot.compose_message(event)
        correct_channels = self.calculate_channels(event.repo.name, event.type)
        for channel in correct_channels:
            self.send_message(channel, message, details)

    def calculate_channels(self, repo: str, event_type: EventType) -> list[str]:
        if repo not in self.subscriptions:
            return []
        else:
            correct_channels: list[str] = []
            for channel in self.subscriptions[repo]:
                if channel.is_subscribed_to(event_type):
                    correct_channels += [channel.name]
            return correct_channels

    @staticmethod
    def compose_message(event: GitHubEvent) -> tuple[str, Optional[str]]:
        message = ""
        details = None

        # TODO: Beautify messages.
        if event.type == EventType.branch_created:
            message = f"{event.repo.name}::\tBranch created by {event.user.name}: `{event.branch.name}`."
        elif event.type == EventType.issue_opened:
            message = (
                f"{event.repo.name}::\t"
                f"Issue opened by {event.user.name}: "
                f"#{event.number} {event.title}"
            )
        elif event.type == EventType.pull_opened:
            message = (
                f"{event.repo.name}::\t"
                f"Pull request opened by {event.user.name}: "
                f"#{event.number} {event.title}"
            )
        elif event.type == EventType.pull_ready:
            message = (
                f"{event.repo.name}::\t"
                f"Review requested on #{event.number} {event.title}: "
                f"{', '.join(reviewer.name for reviewer in event.reviewers)}"
            )
        elif event.type == EventType.push:
            if len(event.commits) == 1:
                message = f"{event.user.name} pushed to {event.branch.name}, one new commit:\n>{event.commits[0]}"
            else:
                message = f"{event.user.name} pushed to {event.branch.name}, {len(event.commits)} new commits:"
                for i, commit in enumerate(event.commits):
                    message += f"\n>{i}. {commit.message}"
        elif event.type == EventType.review:
            message = (
                f"{event.repo.name}::\t"
                f"Review on #{event.number} by {event.reviewers[0].name}: "
                f"STATUS: {event.status}"
            )

        return message, details

    def send_message(self, channel: str, message: str, details: Optional[str]):
        if details is None:
            print(f"Sending {message} to {channel}")
            self.client.chat_postMessage(channel=channel, text=message)
        else:
            response = self.client.chat_postMessage(channel=channel, text=message)
            message_id = response.data["ts"]
            self.client.chat_postMessage(
                channel=channel, text=details, thread_ts=message_id
            )

    # Slash commands related methods
    def run(self, raw_json: MultiDict) -> Optional[dict]:
        json: JSON = JSON.from_multi_dict(raw_json)
        current_channel: str = "#" + json["channel_name"]
        command: str = json["command"]
        args: list[str] = json["text"].split()
        repo: Optional[str] = args[0] if len(args) > 0 else None
        if command == "/subscribe":
            new_events: set[EventType] = {
                SlackBot.convert_str_to_event_type(arg) for arg in args[1:]
            }
            if repo in self.subscriptions:
                channels: set[Channel] = self.subscriptions[repo]
                channel: Optional[Channel] = None
                for subscribed_channel in channels:
                    if subscribed_channel.name == current_channel:
                        channel = subscribed_channel
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
                    old_events = channel.events
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
        elif command == "/unsubscribe" and repo in self.subscriptions:
            channels: set[Channel] = self.subscriptions[repo]
            channel: Optional[Channel] = None
            for subscribed_channel in channels:
                if subscribed_channel.name == current_channel:
                    channel = subscribed_channel
            if channel is not None:
                # If this channel has subscribed to some events
                # from this repo, update the list of events.
                events = channel.events
                for arg in args[1:]:
                    event: EventType = SlackBot.convert_str_to_event_type(arg)
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
        elif command == "/list":
            blocks: list[dict] = []
            for repo in self.subscriptions.keys():
                channels: set[Channel] = self.subscriptions[repo]
                channel: Optional[Channel] = None
                for subscribed_channel in channels:
                    if subscribed_channel.name == current_channel:
                        channel = subscribed_channel
                if channel is None:
                    continue
                events_string = ", ".join(event.name for event in channel.events)
                blocks += [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{repo}*\n" + events_string,
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
        elif command == "/help":
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
                                "1. `bc`: branch_created\n"
                                "2. `bd`: branch_deleted\n"
                                "3. `tc`: tag_created\n"
                                "4. `td`: tag_deleted\n"
                                "5. `prc`: pull_closed\n"
                                "6. `prm`: pull_merged\n"
                                "7. `pro`: pull_opened\n"
                                "8. `prr`: pull_ready\n"
                                "9. `io`: issue_opened\n"
                                "10. `ic`: issue_closed\n"
                                "11. `rv`: review\n"
                                "12. `rc`: review_comment\n"
                                "13. `cc`: commit_comment\n"
                                "14. `fk`: fork\n"
                                "15. `p`: push\n"
                                "16. `rl`: release\n"
                                "17. `sa`: star_added\n"
                                "18. `sr`: star_removed\n"
                            ),
                        },
                    },
                ],
            }
        return

    @staticmethod
    def convert_str_to_event_type(event_name: str) -> EventType:
        for event_type in EventType:
            if event_type.value == event_name:
                return event_type
