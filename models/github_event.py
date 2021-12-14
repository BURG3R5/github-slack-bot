from typing import Optional


class GitHubEvent:
    def __init__(self,
                 event_type: str,
                 repo: str,
                 user: str,
                 number: Optional[int],
                 number_of_commits: Optional[int],
                 branch: Optional[str],
                 status: Optional[str],
                 title: Optional[str],
                 commits: Optional[list[str]],
                 reviewers: Optional[list[str]]):
        self.type = event_type
        self.repo = repo
        self.user = user

        self.number = number
        self.number_of_commits = number_of_commits
        self.branch = branch
        self.status = status
        self.title = title
        self.commits = commits
        self.reviewers = reviewers
