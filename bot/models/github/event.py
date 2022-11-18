"""
Model class that can store all relevant info about all events that the project handles.
"""
from typing import Optional

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

    type: EventType
    repo: Repository
    status: Optional[str]
    issue: Optional[Issue]
    pull_request: Optional[PullRequest]
    ref: Optional[Ref]
    user: Optional[User]
    comments: Optional[list[str]]
    commits: Optional[list[Commit]]
    links: Optional[list[Link]]
    reviewers: Optional[list[User]]

    def __init__(self, event_type: EventType, repo: Repository, **kwargs):
        self.type = event_type
        self.repo = repo

        if "status" in kwargs:
            self.status = kwargs["status"]
        if "issue" in kwargs:
            self.issue = kwargs["issue"]
        if "pull_request" in kwargs:
            self.pull_request = kwargs["pull_request"]
        if "ref" in kwargs:
            self.ref = kwargs["ref"]
        if "user" in kwargs:
            self.user = kwargs["user"]
        if "comments" in kwargs:
            self.comments = kwargs["comments"]
        if "commits" in kwargs:
            self.commits = kwargs["commits"]
        if "links" in kwargs:
            self.links = kwargs["links"]
        if "reviewers" in kwargs:
            self.reviewers = kwargs["reviewers"]

    def __str__(self):
        string = ""
        for var, value in vars(self).items():
            string += var + "="
            if isinstance(value, (list, tuple, set)):
                string += str([str(v) for v in value])
            else:
                string += str(value)
            string += ", "
        return "(" + string[:-2] + ")"
