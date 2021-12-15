import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from slack import WebClient

from models.channel import Channel
from models.github_event import GitHubEvent


class SlackBot:
    def __init__(self):
        load_dotenv(Path('.') / '.env')
        self.client = WebClient(os.environ['SLACK_OAUTH_TOKEN'])
        self.channels: dict[str, list[Channel]] = {
            'fake-rdrive-flutter': [
                Channel('#github-slack-bot', ['push', 'pull']),
                Channel('#bottesting', ['issue'])
            ]
        }

    def inform(self, event: GitHubEvent) -> None:
        message, details = SlackBot.compose_message(event)
        correct_channels = self.calculate_channels(event.repo, event.type)
        for channel in correct_channels:
            self.send_message(channel, message, details)

    def calculate_channels(self, repo: str, event_type: str) -> list[str]:
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
        message = ''
        details = None

        # TODO: Beautify messages.
        if event.type == 'branch':
            message = f"{event.repo}::\t" \
                      f"Branch created by {event.user}: `{event.branch}`."
        elif event.type == 'issue':
            message = f"{event.repo}::\t" \
                      f"Issue opened by {event.user}: " \
                      f"#{event.number} {event.title}"
        elif event.type == 'pull_open':
            message = f"{event.repo}::\t" \
                      f"Pull request opened by {event.user}: " \
                      f"#{event.number} {event.title}"
        elif event.type == 'pull_ready':
            message = f"{event.repo}::\t" \
                      f"Review requested on #{event.number} {event.title}: " \
                      f"{', '.join(event.reviewers)}"
        elif event.type == 'push':
            if event.number_of_commits == 1:
                message = f'{event.user} pushed to {event.branch}, one new commit:\n>{event.commits[0]}'
            else:
                message = f'{event.user} pushed to {event.branch}, {event.number_of_commits} new commits:'
                for i, commit in enumerate(event.commits):
                    message += f'\n>{i}. {commit}'
        elif event.type == 'review':
            message = f"{event.repo}::\t" \
                      f"Review on #{event.number} by {event.reviewers[0]}: " \
                      f"STATUS: {event.status}"

        return message, details

    def send_message(self, channel: str, message: str, details: Optional[str]):
        if details is None:
            self.client.chat_postMessage(channel=channel, text=message)
        else:
            response = self.client.chat_postMessage(channel=channel, text=message)
            message_id = response.data['ts']
            self.client.chat_postMessage(channel=channel, text=details, thread_ts=message_id)
