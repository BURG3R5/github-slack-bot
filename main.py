"""
Execution entrypoint for the github-slack-bot project.

Sets up a `bottle` server with three endpoints: "/", "/github/events" and "/slack/commands".

"/" is used for testing and status checks.

"/github/events" is provided to GitHub Webhooks to POST event info at.
Triggers `manage_github_events` which uses `GitHubPayloadParser.parse` and `SlackBot.inform`.

"/slack/commands" is provided to Slack to POST slash command info at.
Triggers `manage_slack_commands` which uses `SlackBot.run`.
"""
from typing import Any

from bottle import post, run, request, get

from github_parsers import GitHubPayloadParser
from models.github import GitHubEvent
from slack_bot import SlackBot


@get("/")
def test_get() -> str:
    """
    First test endpoint.
    :return: Plaintext confirming server status.
    """
    return "This server is running!"


@post("/")
def test_post() -> str:
    """
    Second test endpoint.
    :return: Status confirmation plaintext containing name supplied in request body.
    """
    try:
        name: str = request.json["name"]
    except KeyError:
        name: str = "unknown"
    return (
        f"This server is working, and to prove it to you, "
        f"I'll guess your name!\nYour name is... {name}!"
    )


@post("/github/events")
def manage_github_events() -> None:
    """
    Uses `GitHubPayloadParser` to parse and cast the payload into a `GitHubEvent`.
    Then uses an instance of `SlackBot` to send appropriate messages to appropriate channels.
    """
    event: GitHubEvent | None = GitHubPayloadParser.parse(
        event_type=request.headers["X-GitHub-Event"],
        raw_json=request.json,
    )
    if event is not None:
        bot.inform(event)


@post("/slack/commands")
def manage_slack_commands() -> dict | None:
    """
    Uses a `SlackBot` instance to run the slash command triggered by the user.
    Optionally returns a Slack message dict as a reply.
    :return: Appropriate response for sent slash command in the form of a dict.
    """
    # Unlike GitHub webhooks, Slack does not send the data in `requests.json`.
    # Instead, the data is passed in `request.forms`.
    response: dict[str, Any] | None = bot.run(raw_json=request.forms)
    return response


bot: SlackBot = SlackBot()
run(host="", port=5556, debug=True)
