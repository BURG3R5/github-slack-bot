from bottle import post, run, request

from github_parsers import GitHubPayloadParser
from slack_bot import SlackBot


@post('/test')
def test():
    name = request.json['name']
    response = 'This server is working, and to prove it to you, ' \
               f"I'll guess your name!\nYour name is... {name}!"
    print(response)
    return response


@post('/github/events')
def manage_github_events():
    GitHubPayloadParser.parse(request.json)


SlackBot()
run(host='', port=5556, debug=True)
