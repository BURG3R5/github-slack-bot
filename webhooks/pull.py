from messages import send_message
from utils.json_utils import JSON


def is_pull_event(json: JSON) -> bool:
    """Determine whether an event is a pull request."""

    return ('pull_request' in json) and \
           (json['action'] in ['opened', 'review_requested'])


def handle_pull_event(json: JSON):
    """Handle received pull events."""

    # Extract valuable info.
    repo = json['repository']['name']
    pr_number = json['number']
    pr_name = json['pull_request']['title']
    action = json['action']

    if action == 'opened':
        user = json['pull_request']['user']['login']

        # Output a summary of the event.
        send_message(f"{repo}::\t"
                     f"Pull request opened by {user}: "
                     f"#{pr_number} {pr_name}")
    elif action == 'review_requested':
        reviewers = [user['login'] for user in json['requested_reviewers']]

        # Output a summary of the event.
        print(f"{repo}::\t"
              f"Review requested on #{pr_number} {pr_name}: "
              f"{', '.join(reviewers)}")
