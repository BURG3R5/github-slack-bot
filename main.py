from bottle import post, run, request

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
    event: GitHubEvent = GitHubPayloadParser.parse(request.json)
    bot.inform(event)


bot: SlackBot = SlackBot()
run(host="", port=5556, debug=True)
