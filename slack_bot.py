import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from slack import WebClient

from models.slack import Channel
from models.github import GitHubEvent, EventType


class SlackBot:
    def __init__(self):
        load_dotenv(Path(".") / ".env")
        self.client = WebClient(os.environ["SLACK_OAUTH_TOKEN"])
        self.channels: dict[str, list[Channel]] = {
            "fake-rdrive-flutter": [
                Channel(
                    "#github-slack-bot",
                    [EventType.branch_created, EventType.push, EventType.pull_opened],
                ),
            ]
        }

    def inform(self, event: GitHubEvent) -> None:
        message, details = SlackBot.compose_message(event)
        correct_channels = self.calculate_channels(event.repo.name, event.type)
        for channel in correct_channels:
            self.send_message(channel, message, details)

    def calculate_channels(self, repo: str, event_type: EventType) -> list[str]:
        if repo not in self.channels:
            return []
        else:
            correct_channels: list[str] = []
            for channel in self.channels[repo]:
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
            print(channel, message)
            self.client.chat_postMessage(channel=channel, text=message)
        else:
            response = self.client.chat_postMessage(channel=channel, text=message)
            message_id = response.data["ts"]
            self.client.chat_postMessage(
                channel=channel, text=details, thread_ts=message_id
            )
