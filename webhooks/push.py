from messages import send_message
from utils.json_utils import JSON


def is_push_event(json: JSON) -> bool:
    """Determine whether an event is a push."""

    return ('commits' in json) and \
           (len(json['commits']) > 0)


def handle_push_event(json: JSON):
    """Handle received push events."""

    # Extract valuable info.
    # Repo
    repo = json['repository']['name']
    base_url = repo["html_url"]

    # User
    user = json[('pusher', 'sender')][('name', 'login')]
    linked_user = f'<https://github.com/{user}|{user}>'

    # Commits
    linked_commits = []
    for commit in json['commits']:
        sha = commit['id']
        commit_link = base_url + f'/commit/{sha}'
        linked_commits.append(f'`<{commit_link}|{sha[:8]}>` - '
                              f'*{commit["message"]}*')
    number_of_commits = len(linked_commits)

    # Branch
    branch = json['ref'].split('/')[-1]
    linked_branch = f'`<{base_url}/tree/{branch}|{branch}>`'

    # Output a summary of the event.
    if number_of_commits == 1:
        message = f'{linked_user} pushed to {linked_branch}, one new commit:\n>{linked_commits[0]}'
    else:
        message = f'{linked_user} pushed to {linked_branch}, {number_of_commits} new commits:'
        for i, commit in enumerate(linked_commits):
            message += f'\n>{i}. {commit}'
    send_message(message)
