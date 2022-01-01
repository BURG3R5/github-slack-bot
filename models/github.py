"""
Collection of models related to the GitHub portion of the project.
"""

import enum
from typing import Optional, Literal

from models.link import Link


class Commit:
    """
    Model for a Git commit.

    :param message: The commit message.
    :param sha: The commit's SHA.
    :param link: The commit's link on GitHub.
    """

    def __init__(
        self,
        message: Optional[str] = None,
        sha: Optional[str] = None,
        link: Optional[str] = None,
    ):
        self.message = message
        self.sha = sha
        self.link = link


class EventType(enum.Enum):
    """
    Enum for easy access to all types of GitHub events handled by the project.
    """

    # Ref
    branch_created = "bc"
    branch_deleted = "bd"
    tag_created = "tc"
    tag_deleted = "td"

    # PR/Issue
    pull_closed = "prc"
    pull_merged = "prm"
    pull_opened = "pro"
    pull_ready = "prr"
    issue_opened = "io"
    issue_closed = "ic"

    # Review
    review = "rv"
    review_comment = "rc"

    # Discussion
    commit_comment = "cc"
    issue_comment = "ic"

    # Misc.
    fork = "fk"
    push = "p"
    release = "rl"
    star_added = "sa"
    star_removed = "sr"


class Ref:
    """
    Model for a Git ref (branch/tag).

    :param name: Name of the ref.
    :param ref_type: "branch" or "tag".
    """

    def __init__(
        self,
        name: str,
        ref_type: Literal["branch", "tag"] = "branch",
        **kwargs,
    ):
        self.name = name
        self.link: Optional[str] = kwargs.get("link", None)
        self.type = ref_type


class Repository:
    """
    Model for a GitHub repository.

    :param name: Name of the repo.
    :keyword link: Link to the repo on GitHub.
    """

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.link: Optional[str] = kwargs.get("link", None)


class User:
    """
    Model for a GitHub user.

    :param name: Username/id of the user.
    :keyword link: Link to the user's GitHub profile.
    """

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.link = kwargs.get("link", f"https://github.com/{name}")


# pylint: disable-next=too-many-instance-attributes
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

        self.number: Optional[int] = kwargs.get("number", None)

        self.status: Optional[str] = kwargs.get("status", None)
        self.title: Optional[str] = kwargs.get("title", None)

        self.ref: Optional[Ref] = kwargs.get("ref", None)
        self.user: Optional[User] = kwargs.get("user", None)

        self.comments: Optional[list[str]] = kwargs.get("comments", None)

        self.commits: Optional[list[Commit]] = kwargs.get("commits", None)
        self.links: Optional[list[Link]] = kwargs.get("links", None)
        self.reviewers: Optional[list[User]] = kwargs.get("reviewers", None)
