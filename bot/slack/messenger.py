"""
Contains the `Messenger` class, which sends Slack messages according to GitHub events.
"""

from slack.web.client import WebClient  # pylint: disable=no-name-in-module

from ..models.github import EventType
from ..models.github.event import GitHubEvent
from ..models.slack import Channel


class Messenger:
    """
    Sends Slack messages according to received GitHub events.
    """

    def __init__(self, token: str):
        self.client: WebClient = WebClient(token)
        # Dummy initialization. Overridden in `SlackBot.__init__()`.
        self.subscriptions: dict[str, set[Channel]] = {}

    def inform(self, event: GitHubEvent):
        """
        Notify the subscribed channels about the passed event.
        :param event: `GitHubEvent` containing all relevant data about the event.
        """
        message, details = Messenger.compose_message(event)
        correct_channels: list[str] = self.calculate_channels(
            repo=event.repo.name,
            event_type=event.type,
        )
        for channel in correct_channels:
            self.send_message(channel, message, details)

    def calculate_channels(self, repo: str,
                           event_type: EventType) -> list[str]:
        """
        Determines the Slack channels that need to be notified about the passed event.
        :param repo: Name of the repository that the event was triggered in.
        :param event_type: Enum-ized type of event.
        :return: `list` of names of channels that are subscribed to the repo+event_type.
        """
        repo_name: str = repo.split("/")[-1]
        if repo not in self.subscriptions:
            if repo_name not in self.subscriptions:
                return []
            repo = repo_name
        correct_channels: list[str] = [
            channel.name for channel in self.subscriptions[repo]
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

        if event.type == EventType.BRANCH_CREATED:
            message = f"Branch created by {event.user}: `{event.ref}`"
        elif event.type == EventType.BRANCH_DELETED:
            message = f"Branch deleted by {event.user}: `{event.ref}`"
        elif event.type == EventType.COMMIT_COMMENT:
            message = f"<{event.links[0].url}|Comment on `{event.commits[0].sha}`> by {event.user}\n>{event.comments[0]}"
        elif event.type == EventType.FORK:
            message = f"<{event.links[0].url}|Repository forked> by {event.user}"
        elif event.type == EventType.ISSUE_OPENED:
            message = f"Issue opened by {event.user}:\n>{event.issue}"
        elif event.type == EventType.ISSUE_CLOSED:
            message = f"Issue closed by {event.user}:\n>{event.issue}"
        elif event.type == EventType.ISSUE_COMMENT:
            type_of_discussion = "Issue" if "issue" in event.issue.link else "PR"
            message = f"<{event.links[0].url}|Comment on {type_of_discussion} #{event.issue.number}> by {event.user}\n>{event.comments[0]}"
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
            details = "\n".join(f"• {commit.message}"
                                for commit in event.commits)
        elif event.type == EventType.RELEASE:
            message = f"Release {event.status} by {event.user}: `{event.ref}`"
        elif event.type == EventType.REVIEW:
            message = (
                f"Review on <{event.pull_request.link}|#{event.pull_request.number}> "
                f"by {event.reviewers[0]}:\n>Status: "
                f"{'Approved' if event.status == 'approved' else 'Changed requested'}"
            )
        elif event.type == EventType.REVIEW_COMMENT:
            message = f"<{event.links[0].url}|Comment on PR #{event.pull_request.number}> by {event.user}\n>{event.comments[0]}"
        elif event.type == EventType.STAR_ADDED:
            message = f"`{event.repo.name}` received a star from `{event.user}`."
        elif event.type == EventType.STAR_REMOVED:
            message = f"`{event.repo.name}` lost a star from `{event.user}`."
        elif event.type == EventType.TAG_CREATED:
            message = f"Tag created by {event.user}: `{event.ref}`"
        elif event.type == EventType.TAG_DELETED:
            message = f"Tag deleted by {event.user}: `{event.ref}`"

        return message, details

    def send_message(self, channel: str, message: str, details: str | None):
        """
        Sends the passed message to the passed channel.
        Also, optionally posts `details` in a thread under the main message.
        :param channel: Channel to send the message to.
        :param message: Main message, briefly summarizing the event.
        :param details: Text to be sent as a reply to the main message. Verbose stuff goes here.
        """
        print(
            f"\n\nSENDING:\n{message}\n\nWITH DETAILS:\n{details}\n\nTO: {channel}"
        )
        if details is None:
            self.client.chat_postMessage(
                channel=channel,
                blocks=[{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message,
                    },
                }],
                unfurl_links=False,
                unfurl_media=False,
            )
        else:
            response = self.client.chat_postMessage(
                channel=channel,
                blocks=[{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message,
                    },
                }],
                unfurl_links=False,
                unfurl_media=False,
            )
            message_id = response.data["ts"]
            self.client.chat_postMessage(
                channel=channel,
                blocks=[{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": details,
                    },
                }],
                thread_ts=message_id,
                unfurl_links=False,
                unfurl_media=False,
            )
