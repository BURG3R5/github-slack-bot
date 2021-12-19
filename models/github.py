import enum
from typing import Optional, Literal

from models.link import Link


class Commit:
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
    # Ref
    branch_created = "branch created"
    branch_deleted = "branch deleted"
    tag_created = "tag created"
    tag_deleted = "tag deleted"

    # PR/Issue
    pull_closed = "pull request closed"
    pull_merged = "pull request merged"
    pull_opened = "pull request opened"
    pull_ready = "pull request marked ready for review"
    issue_opened = "issue opened"
    issue_closed = "issue closed"

    push = "code pushed"

    review = "R"

    # Discussion
    commit_comment = "comment on commit"

    # Misc.
    fork = "repository forked"
    release = "release"
    star_added = "repository starred"
    star_removed = "repository unstarred"


class Ref:
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
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.link: Optional[str] = kwargs.get("link", None)


class User:
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.link = kwargs.get("link", f"https://github.com/{name}")


class GitHubEvent:
    def __init__(self, event_type: EventType, repo: Repository, **kwargs):
        self.type = event_type
        self.repo = repo

        self.number: Optional[int] = kwargs.get("number", None)

        self.status: Optional[str] = kwargs.get("status", None)
        self.title: Optional[str] = kwargs.get("title", None)

        self.branch: Optional[Ref] = kwargs.get("branch", None)
        self.user: Optional[User] = kwargs.get("user", None)

        self.comments: Optional[list[str]] = kwargs.get("comments", None)

        self.commits: Optional[list[Commit]] = kwargs.get("commits", None)
        self.links: Optional[list[Link]] = kwargs.get("links", None)
        self.reviewers: Optional[list[User]] = kwargs.get("reviewers", None)
