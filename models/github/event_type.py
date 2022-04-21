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
    ISSUE_OPENED = ("iso", "An Issue was opened")
    ISSUE_CLOSED = ("isc", "An Issue was closed")

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


def convert_keywords_to_events(keywords: list[str]) -> set[EventType]:
    """
    Returns a  set of `EventType` members corresponding to the passed keywords.
    If no `EventType` is matched, returns an empty set.
    :param keywords: List of short strings representing the events.
    :return: Set of `EventType` members corresponding to the keywords.
    """
    if len(keywords) == 0 or "default" in keywords:
        return {
            EventType.BRANCH_CREATED,
            EventType.TAG_CREATED,
            EventType.PULL_OPENED,
            EventType.ISSUE_OPENED,
            EventType.REVIEW,
            EventType.COMMIT_COMMENT,
            EventType.ISSUE_COMMENT,
            EventType.PUSH,
            EventType.STAR_ADDED,
        }
    if "all" in keywords or "*" in keywords:
        return set(EventType)
    return {
        event_type
        for event_type in EventType
        for keyword in keywords
        if event_type.keyword == keyword
    }
