"""
Execution entrypoint for the project.

Sets up a `bottle` server with three endpoints: "/", "/github/events" and "/slack/commands".

"/" is used for testing and status checks.

"/github/events" is provided to GitHub Webhooks to POST event info at.
Triggers `manage_github_events` which uses `GitHubApp.parse` and `SlackBot.inform`.

"/slack/commands" is provided to Slack to POST slash command info at.
Triggers `manage_slack_commands` which uses `SlackBot.run`.
"""

import os
from pathlib import Path
from typing import Any, Optional, Union

import sentry_sdk
from bottle import get, post, request
from bottle import response as http_response
from bottle import run
from dotenv import load_dotenv
from sentry_sdk.integrations.bottle import BottleIntegration

from bot.github import GitHubApp
from bot.models.github.event import GitHubEvent
from bot.slack import SlackBot
from bot.slack.templates import error_message
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
    Uses `GitHubApp` to verify, parse and cast the payload into a `GitHubEvent`.
    Then uses an instance of `SlackBot` to send appropriate messages to appropriate channels.
    """

    is_valid_request, message = github_app.verify(request)
    if not is_valid_request:
        http_response.status = "400 Bad Request"
        return message

    event: Optional[GitHubEvent] = github_app.parse(
        event_type=request.headers["X-GitHub-Event"],
        raw_json=request.json,
    )

    if event is not None:
        slack_bot.inform(event)


@post("/slack/commands")
def manage_slack_commands() -> Union[dict, str, None]:
    """
    Uses a `SlackBot` instance to run the slash command triggered by the user.
    Optionally returns a Slack message dict as a reply.
    :return: Appropriate response for received slash command in Slack block format.
    """

    is_valid_request, message = slack_bot.verify(
        body=request.body,
        headers=request.headers,
    )
    if not is_valid_request:
        return error_message(f"⚠️ Couldn't fulfill your request: {message}")

    # Unlike GitHub webhooks, Slack does not send the data in `requests.json`.
    # Instead, the data is passed in `request.forms`.
    response: dict[str, Any] | None = slack_bot.run(raw_json=request.forms)
    return response


@get("/github/auth")
def initiate_auth():
    github_app.redirect_to_oauth_flow(request.params.get("state"))


@get("/github/auth/redirect")
def complete_auth():
    return github_app.set_up_webhooks(
        code=request.query.get("code"),
        state=request.params.get("state"),
    )


if __name__ == "__main__":
    load_dotenv(Path(".") / ".env")

    debug = os.environ["DEBUG"] == "1"
    port = int(os.environ.get("CONTAINER_PORT", 5000))

    if (not debug) and ("SENTRY_DSN" in os.environ):
        sentry_sdk.init(
            dsn=os.environ["SENTRY_DSN"],
            integrations=[BottleIntegration()],
        )

    slack_bot = SlackBot(
        token=os.environ["SLACK_OAUTH_TOKEN"],
        logger=Logger(int(os.environ.get("LOG_LAST_N_COMMANDS", 100))),
        base_url=os.environ["BASE_URL"],
        secret=os.environ["SLACK_SIGNING_SECRET"],
        bot_id=os.environ["SLACK_BOT_ID"],
    )

    github_app = GitHubApp(
        base_url=os.environ["BASE_URL"],
        client_id=os.environ["GITHUB_APP_CLIENT_ID"],
        client_secret=os.environ["GITHUB_APP_CLIENT_SECRET"],
    )

    run(host="", port=port, debug=debug)
