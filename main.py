from bottle import post, run, request, get

from github_parsers import GitHubPayloadParser
from models.github import GitHubEvent
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
    event: GitHubEvent = GitHubPayloadParser.parse(
        event_type=request.headers["X-GitHub-Event"], raw_json=request.json
    )
    bot.inform(event)


@post("/slack/commands")
def manage_slack_commands():
    bot.run(request.forms)


bot: SlackBot = SlackBot()
run(host="", port=5556, debug=True)
