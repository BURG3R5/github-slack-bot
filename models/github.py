"""
Collection of models related to the GitHub portion of the project.
"""

import enum
from typing import Literal

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
        message: str | None = None,
        sha: str | None = None,
        link: str | None = None,
    ):
        self.message = message
        self.sha = sha
        self.link = link


class EventType(enum.Enum):
    """
    Enum for easy access to all types of GitHub events handled by the project.
    """

    # Ref
    BRANCH_CREATED = ("bc", "Branch was created")
    BRANCH_DELETED = ("bd", "Branch was deleted")
    TAG_CREATED = ("tc", "Tag was created")
    TAG_DELETED = ("td", "Tag was deleted")

    # PR/Issue
    PULL_CLOSED = ("prc", "Pull Request was closed")
    PULL_MERGED = ("prm", "Pull Request was merged")
    PULL_OPENED = ("pro", "Pull Request was opened")
    PULL_READY = ("prr", "Pull Request is ready")
    ISSUE_OPENED = ("io", "Issue was opened")
    ISSUE_CLOSED = ("ic", "Issue was closed")

    # Review
    REVIEW = ("rv", "Review was submitted on a Pull Request")
    REVIEW_COMMENT = ("rc", "Comment was added to a Review")

    # Discussion
    COMMIT_COMMENT = ("cc", "Comment was made on a commit")
    ISSUE_COMMENT = ("ic", "Comment was made on an Issue")

    # Misc.
    FORK = ("fk", "Repository was forked by user")
    PUSH = ("p", "Commit was pushed")
    RELEASE = ("rl", "New release was published")
    STAR_ADDED = ("sa", "Star was added to repository")
    STAR_REMOVED = ("sr", "Star was removed from repository")

    def __init__(self, keyword, docs):
        self.keyword = keyword
        self.docs = docs


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
        self.link: str | None = kwargs.get("link", None)
        self.type = ref_type


class Repository:
    """
    Model for a GitHub repository.

    :param name: Name of the repo.
    :keyword link: Link to the repo on GitHub.
    """

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.link: str | None = kwargs.get("link", None)


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

        self.number: int | None = kwargs.get("number", None)

        self.status: str | None = kwargs.get("status", None)
        self.title: str | None = kwargs.get("title", None)

        self.ref: Ref | None = kwargs.get("ref", None)
        self.user: User | None = kwargs.get("user", None)

        self.comments: list[str] | None = kwargs.get("comments", None)

        self.commits: list[Commit] | None = kwargs.get("commits", None)
        self.links: list[Link] | None = kwargs.get("links", None)
        self.reviewers: list[User] | None = kwargs.get("reviewers", None)
