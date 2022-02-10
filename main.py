from typing import Optional

from bottle import post, run, request, get

from github_parsers import GitHubPayloadParser
from models.github import GitHubEvent
from slack_bot import SlackBot


@get("/")
def test_get():
    return "This server is running!"


@post("/")
def test_post():
    return (
        f"This server is working, and to prove it to you, "
        f"I'll guess your name!\nYour name is... {request.json['name']}!"
    )


@post("/github/events")
def manage_github_events():
    event: Optional[GitHubEvent] = GitHubPayloadParser.parse(
        event_type=request.headers["X-GitHub-Event"],
        raw_json=request.json,
    )
    if event is not None:
        bot.inform(event)


@post("/slack/commands")
def manage_slack_commands() -> Optional[dict]:
    response: Optional[dict] = bot.run(raw_json=request.forms)
    if response is not None:
        return response
    return None


bot: SlackBot = SlackBot()
run(host="", port=5556, debug=True, reloader=True)
