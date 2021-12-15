import os
from pathlib import Path

from bottle import post, run, request
from dotenv import load_dotenv

from github_parsers import GitHubPayloadParser
from models.github_event import GitHubEvent
from slack_bot import SlackBot


@post("/test")
def test():
    name: str = request.json["name"]
    response: str = (
        "This server is working, and to prove it to you, "
        f"I'll guess your name!\nYour name is... {name}!"
    )
    print(response)
    return response


@post("/github/events")
def manage_github_events():
    event: GitHubEvent = GitHubPayloadParser.parse(request.json)
    bot.inform(event)


load_dotenv(Path(".") / ".env")
bot: SlackBot = SlackBot()
if os.environ.get("APP_LOCATION") == "heroku":
    run(host="0.0.0.0", port=int(os.environ.get("PORT", 5556)))
else:
    run(host="localhost", port=5556, debug=True)
