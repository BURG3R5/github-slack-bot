"""
Execution entrypoint for the github-slack-bot project.

Sets up a `bottle` server with three endpoints: "/", "/github/events" and "/slack/commands".

"/" is used for testing and status checks.

"/github/events" is provided to GitHub Webhooks to POST event info at.
Triggers `manage_github_events` which uses `GitHubListener.parse` and `SlackBot.inform`.

"/slack/commands" is provided to Slack to POST slash command info at.
Triggers `manage_slack_commands` which uses `SlackBot.run`.
"""

import os
from pathlib import Path
from typing import Any

import sentry_sdk
from bottle import get, post, request
from bottle import response as http_response
from bottle import run
from dotenv import load_dotenv
from sentry_sdk.integrations.bottle import BottleIntegration

from bot.github.authentication import GitHubOAuth
from bot.github.github_parsers import GitHubListener
from bot.models.github.event import GitHubEvent
from bot.slack import SlackBot
from bot.utils.log import Logger


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
        name: str = "(empty JSON)"
    except TypeError:
        name: str = "(invalid JSON)"
    return (f"This server is working, and to prove it to you, "
            f"I'll guess your name!\nYour name is... {name}!")


@post("/github/events")
def manage_github_events():
    """
    Uses `GitHubListener` to verify, parse and cast the payload into a `GitHubEvent`.
    Then uses an instance of `SlackBot` to send appropriate messages to appropriate channels.
    """

    if listener.secret is not None:
        is_valid_request, error_message = listener.check_validity(
            body=request.body,
            headers=request.headers,
        )
        if not is_valid_request:
            http_response.status = "400 Bad Request"
            return error_message

    event: GitHubEvent | None = listener.parse(
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
    :return: Appropriate response for received slash command in Slack block format.
    """
    # Unlike GitHub webhooks, Slack does not send the data in `requests.json`.
    # Instead, the data is passed in `request.forms`.
    response: dict[str, Any] | None = bot.run(raw_json=request.forms)
    return response


@get("/github/auth")
def initiate_auth():
    GitHubOAuth.redirect_to_oauth_flow(request.params.get("repository"))


@get("/github/auth/redirect/<owner>/<repo>")
def complete_auth(owner, repo):
    return GitHubOAuth.set_up_webhooks(
        code=request.query.get("code"),
        repository=f"{owner}/{repo}",
    )


if __name__ == "__main__":
    load_dotenv(Path(".") / ".env")
    debug: bool = os.environ["DEBUG"] == "1"

    if not debug:
        sentry_sdk.init(
            dsn=os.environ["SENTRY_DSN"],
            integrations=[BottleIntegration()],
        )

    listener = GitHubListener(os.environ.get("GITHUB_WEBHOOK_SECRET"))

    bot: SlackBot = SlackBot(
        token=os.environ["SLACK_OAUTH_TOKEN"],
        logger=Logger(int(os.environ["LOG_LAST_N_COMMANDS"] or 100)),
    )

    run(host="", port=int(os.environ["CONTAINER_PORT"]), debug=debug)
