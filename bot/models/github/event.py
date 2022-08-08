"""
Model class that can store all relevant info about all events that the project handles.
"""

from ..link import Link
from . import Commit, EventType, Issue, PullRequest, Ref, Repository, User


class GitHubEvent:
    """
    Model class that can store all relevant info about all events that the project handles.

    :param event_type: Enum-ized type of the event in question.
    :param repo: Repository where the event originated.
    :keyword user: GitHub user who triggered the event.
    :keyword ref: Branch or tag ref related to the event.

    :keyword number: Number of the PR/Issue related to the event.
    :keyword title: Title of the PR/Issue related to the event.

    :keyword status: Status of the review where the event originated.
    :keyword commits: List of commits send with the event.
    :keyword comments: List of comments related to the event.
    :keyword reviewers: List of reviewers mentioned in the event.
    :keyword links: List of miscellaneous links.
    """

    def __init__(self, event_type: EventType, repo: Repository, **kwargs):
        self.type = event_type
        self.repo = repo

        self.status: str | None = kwargs.get("status", None)

        self.issue: Issue | None = kwargs.get("issue", None)
        self.pull_request: PullRequest | None = kwargs.get(
            "pull_request",
            None,
        )
        self.ref: Ref | None = kwargs.get("ref", None)
        self.user: User | None = kwargs.get("user", None)

        self.comments: list[str] | None = kwargs.get("comments", None)

        self.commits: list[Commit] | None = kwargs.get("commits", None)
        self.links: list[Link] | None = kwargs.get("links", None)
        self.reviewers: list[User] | None = kwargs.get("reviewers", None)

    def __str__(self):
        return f"<{self.type}|{self.repo}>"
