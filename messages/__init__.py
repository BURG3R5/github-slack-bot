import os
from pathlib import Path

import slack
from dotenv import load_dotenv

client: slack.WebClient


def init() -> None:
    global client
    load_dotenv(Path('.') / '.env')
    client = slack.WebClient(os.environ['SLACK_OAUTH_TOKEN'])


def send_message(message='', channel='#github-bot-testing', details=''):
    if details == '':
        client.chat_postMessage(channel=channel, text=message)
    else:
        response = client.chat_postMessage(channel=channel, text=message)
        message_id = response.data['ts']
        client.chat_postMessage(channel=channel, text=details, thread_ts=message_id)
