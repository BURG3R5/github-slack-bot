"""
Steps:
1) Go to https://api.slack.com/authentication/config-tokens#creating
2) Create App config token.
3) Paste it below.
4) Write url of your server.
5) Run this script.

"""
import json
import os
import urllib.parse

import requests

url = "<URL>"
token = "<YOUR_TOKEN>"
app_id = os.environ["SLACK_BOT_ID"]


def update_app_manifest():
    prev_manifest: dict = get_prev_manifest()

    for i in range(4):
        prev_manifest["features"]["slash_commands"][i].update({"url": url})

    params = {
        "app_id": app_id,
        "manifest": json.dumps(prev_manifest),
    }
    endpoint = "https://slack.com/api/apps.manifest.update/?" + urllib.parse.urlencode(
        params)
    response = requests.post(
        endpoint,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )


def get_prev_manifest():
    endpoint = "https://slack.com/api/apps.manifest.export/?app_id=" + app_id
    response = requests.post(
        endpoint,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )

    return response.json()["manifest"]


def rotate_token(refresh_token):
    endpoint = "https://slack.com/api/tooling.tokens.rotate/?" + urllib.parse.urlencode(
        refresh_token)
    response = requests.post(
        endpoint,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    return response.json()["token"], response.json()["refresh_token"]


if __name__ == "__main__":
    update_app_manifest()
