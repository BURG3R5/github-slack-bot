import enum
from typing import Literal

from models.link import Link


class Commit:
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
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.link: str | None = kwargs.get("link", None)


class User:
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.link = kwargs.get("link", f"https://github.com/{name}")


# pylint: disable-next=too-many-instance-attributes
class GitHubEvent:
    def __init__(self, event_type: EventType, repo: Repository, **kwargs):
        self.type = event_type
        self.repo = repo

        self.number: int | None = kwargs.get("number", None)

        self.status: str | None = kwargs.get("status", None)
        self.title: str | None = kwargs.get("title", None)

        self.branch: Ref | None = kwargs.get("branch", None)
        self.user: User | None = kwargs.get("user", None)

        self.comments: list[str] | None = kwargs.get("comments", None)

        self.commits: list[Commit] | None = kwargs.get("commits", None)
        self.links: list[Link] | None = kwargs.get("links", None)
        self.reviewers: list[User] | None = kwargs.get("reviewers", None)
