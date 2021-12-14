from typing import Optional


class GitHubEvent:
    def __init__(self, event_type: str, repo: str, user: str, **kwargs):
        self.type = event_type
        self.repo = repo
        self.user = user

        self.number: Optional[int] = kwargs.get('number', None)
        self.number_of_commits: Optional[int] = kwargs.get('number_of_commits', None)
        self.branch: Optional[str] = kwargs.get('branch', None)
        self.status: Optional[str] = kwargs.get('status', None)
        self.title: Optional[str] = kwargs.get('title', None)
        self.commits: Optional[list[str]] = kwargs.get('commits', None)
        self.reviewers: Optional[list[str]] = kwargs.get('reviewers', None)
