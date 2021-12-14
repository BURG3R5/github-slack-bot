from messages import send_message
from utils.json_utils import JSON


def is_review_event(json: JSON) -> bool:
    """Determine whether an event is an review."""

    return ('review' in json) and \
           (json['action'] == 'submitted') and \
           (json['review']['state'].lower() in ['approved', 'changes_requested'])


def handle_review_event(json: JSON):
    """Handle received review events."""

    # Extract valuable info.
    repo = json['repository']['name']
    reviewer = json['review']['user']['login']
    state = json['review']['state'].lower()
    pr_number = json['pull_request']['number']

    # Output a summary of the event.
    send_message(f"{repo}::\t"
                 f"Review on #{pr_number} by {reviewer}: "
                 f"STATUS: {state}")
