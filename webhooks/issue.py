from messages import send_message
from utils.json_utils import JSON


def is_issue_event(json: JSON) -> bool:
    """Determine whether an event is an issue."""

    return ('issue' in json) and \
           (json['action'] == 'opened')


def handle_issue_event(json: JSON):
    """Handle received issue events."""

    # Extract valuable info.
    repo = json['repository']['name']
    issue_number = json['issue']['number']
    issue_title = json['issue']['title']
    user = json['issue']['user']['login']

    # Output a summary of the event.
    send_message(f"{repo}::\t"
                 f"Issue opened by {user}: "
                 f"#{issue_number} {issue_title}")
