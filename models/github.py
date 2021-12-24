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
    branch_created = ("bc", "Branch was created")
    branch_deleted = ("bd", "Branch was deleted")
    tag_created = ("tc", "Tag was created")
    tag_deleted = ("td", "Tag was deleted")

    # PR/Issue
    pull_closed = ("prc", "Pull Request was closed")
    pull_merged = ("prm", "Pull Request was merged")
    pull_opened = ("pro", "Pull Request was opened")
    pull_ready = ("prr", "Pull Request is ready")
    issue_opened = ("io", "Issue was opened")
    issue_closed = ("ic", "Issue was closed")

    # Review
    review = ("rv", "Review was submitted on a Pull Request")
    review_comment = ("rc", "Comment was added to a Review")

    # Discussion
    commit_comment = ("cc", "Comment was made on a commit")
    issue_comment = ("ic", "Comment was made on an Issue")

    # Misc.
    fork = ("fk", "Repository was forked by user")
    push = ("p", "Commit was pushed")
    release = ("rl", "New release was published")
    star_added = ("sa", "Star was added to repository")
    star_removed = ("sr", "Star was removed from repository")

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
