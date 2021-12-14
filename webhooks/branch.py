from messages import send_message
from utils.json_utils import JSON


def is_branch_event(json: JSON) -> bool:
    """Determine whether an event is a branch event."""

    return 'ref_type' in json and \
           json['ref_type'] == 'branch' and \
           json['pusher_type'] == 'user'


def handle_branch_event(json: JSON):
    """Handle received branch events."""

    # Extract valuable info.
    repo = json['repository']['name']
    user = json['sender'][('name', 'login')]
    branch = json['ref'].split('/')[-1]

    # Output a summary of the event.
    send_message(f"{repo}::\t"
                 f"Branch created by {user}: `{branch}`.")
