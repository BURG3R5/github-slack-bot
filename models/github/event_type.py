"""
Enum for easy access to all types of GitHub events handled by the project.
"""

from enum import Enum


class EventType(Enum):
    """
    Enum for easy access to all types of GitHub events handled by the project.
    """

    # Ref
    BRANCH_CREATED = ("bc", "A Branch was created")
    BRANCH_DELETED = ("bd", "A Branch was deleted")
    TAG_CREATED = ("tc", "A Tag was created")
    TAG_DELETED = ("td", "A Tag was deleted")

    # PR/Issue
    PULL_CLOSED = ("prc", "A Pull Request was closed")
    PULL_MERGED = ("prm", "A Pull Request was merged")
    PULL_OPENED = ("pro", "A Pull Request was opened")
    PULL_READY = ("prr", "A Pull Request is ready")
    ISSUE_OPENED = ("io", "An Issue was opened")
    ISSUE_CLOSED = ("ic", "An Issue was closed")

    # Review
    REVIEW = ("rv", "A Review was given on a Pull Request")
    REVIEW_COMMENT = ("rc", "A Comment was added to a Review")

    # Discussion
    COMMIT_COMMENT = ("cc", "A Comment was made on a Commit")
    ISSUE_COMMENT = ("ic", "A Comment was made on an Issue")

    # Misc.
    FORK = ("fk", "Repository was forked by a user")
    PUSH = ("p", "One or more Commits were pushed")
    RELEASE = ("rl", "A new release was published")
    STAR_ADDED = ("sa", "A star was added to repository")
    STAR_REMOVED = ("sr", "A star was removed from repository")

    def __init__(self, keyword, docs):
        self.keyword = keyword
        self.docs = docs


def convert_str_to_event_type(event_keyword: str) -> EventType | None:
    """
    Returns the `EventType` member corresponding to the passed keyword.
    If no `EventType` is matched, returns `None`.
    :param event_keyword: Short string representing the event.
    :return: `EventType` member corresponding to the keyword.
    """
    for event_type in EventType:
        if event_type.value == event_keyword:
            return event_type
    print("Event not in enum")
    return None
