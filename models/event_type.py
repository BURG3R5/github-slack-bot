import enum


class EventType(enum.Enum):
    branch_created = "branch created"
    # branch_deleted = 'BD'
    tag_created = "tag created"
    # tag_deleted = 'TD'

    pull_opened = "pull request opened"
    pull_ready = "pull request marked ready for review"
    # pull_merged = 'pull request merged'
    # pull_closed = 'pull request closed'
    issue_opened = "issue opened"
    issue_closed = "issue closed"

    push = "code pushed"

    review = "R"
