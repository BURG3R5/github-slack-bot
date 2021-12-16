from typing import Optional

from models.event_type import EventType


class GitHubEvent:
    def __init__(self, event_type: EventType, repo: str, **kwargs):
        self.type = event_type
        self.repo = repo

        self.number: Optional[int] = kwargs.get("number", None)
        self.number_of_commits: Optional[int] = kwargs.get("number_of_commits", None)
        self.branch: Optional[str] = kwargs.get("branch", None)
        self.status: Optional[str] = kwargs.get("status", None)
        self.title: Optional[str] = kwargs.get("title", None)
        self.user: Optional[str] = kwargs.get("user", None)
        self.comments: Optional[list[str]] = kwargs.get("comments", None)
        self.commits: Optional[list[str]] = kwargs.get("commits", None)
        self.links: Optional[list[str]] = kwargs.get("links", None)
        self.reviewers: Optional[list[str]] = kwargs.get("reviewers", None)
