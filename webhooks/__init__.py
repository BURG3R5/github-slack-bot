from utils.json_utils import JSON
from .branch import handle_branch_event, is_branch_event
from .issue import handle_issue_event, is_issue_event
from .pull import handle_pull_event, is_pull_event
from .push import handle_push_event, is_push_event
from .review import handle_review_event, is_review_event


def parse_github_event(raw_json):
    """Parse received JSON and call appropriate handler."""
    json = JSON(raw_json)

    if is_push_event(json):
        handle_push_event(json)
    elif is_branch_event(json):
        handle_branch_event(json)
    elif is_pull_event(json):
        handle_pull_event(json)
    elif is_issue_event(json):
        handle_issue_event(json)
    elif is_review_event(json):
        handle_review_event(json)
