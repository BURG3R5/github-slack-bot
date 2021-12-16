import enum
from typing import Optional

from models.github import Commit, Ref, User, Repository
from models.slack import Link


class EventType(enum.Enum):
    # Ref
    branch_created = "branch created"
    # branch_deleted = 'BD'
    tag_created = "tag created"
    # tag_deleted = 'TD'

    # PR/Issue
    pull_opened = "pull request opened"
    pull_ready = "pull request marked ready for review"
    # pull_merged = 'pull request merged'
    # pull_closed = 'pull request closed'
    issue_opened = "issue opened"
    issue_closed = "issue closed"

    push = "code pushed"

    review = "R"

    # Discussion
    commit_comment = "comment on commit"


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
