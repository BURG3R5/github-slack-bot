"""
Steps:
1) Go to https://api.slack.com/authentication/config-tokens#creating
2) Create App config tokens
3) Paste your tokens and url in ../.env
4) Run this script

"""

import json
import os
from typing import Any

import dotenv
import requests


def update_app_manifest() -> tuple[int, bool]:
    prev_manifest = get_prev_manifest()

    url = os.environ["BASE_URL"]
    if url.startswith("http://"):
        url = "https://" + url[7:]
    elif not url.startswith("https://"):
        url = "https://" + url
    if url.endswith('/'):
        url = url[:-1]

    url += "/slack/commands"

    for i in range(4):
        prev_manifest["features"]["slash_commands"][i].update({"url": url})

    endpoint = "https://slack.com/api/apps.manifest.update/"
    response = requests.post(
        endpoint,
        params={
            "app_id": os.environ["SLACK_APP_ID"],
            "manifest": json.dumps(prev_manifest),
        },
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
    )
    return response.status_code, response.json()["ok"]


def get_prev_manifest() -> dict[str, Any]:
    endpoint = f"https://slack.com/api/apps.manifest.export/"
    response = requests.post(
        endpoint,
        params={
            "app_id": os.environ["SLACK_APP_ID"],
        },
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
    ).json()

    if response["ok"]:
        return response["manifest"]
    else:
        print(response)
        raise Exception()


def rotate_token() -> str:
    endpoint = "https://slack.com/api/tooling.tokens.rotate/"
    response = requests.post(
        endpoint,
        params={
            "refresh_token": os.environ["MANIFEST_REFRESH_TOKEN"]
        },
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    ).json()
    if response["ok"]:
        dotenv.set_key(
            dotenv_path=dotenv.find_dotenv(),
            key_to_set="MANIFEST_REFRESH_TOKEN",
            value_to_set=response["refresh_token"],
        )
        return response["token"]
    else:
        print(response)
        raise Exception()


if __name__ == "__main__":
    dotenv.load_dotenv(dotenv.find_dotenv())

    access_token = rotate_token()
    status_code, is_okay = update_app_manifest()
    print(status_code, is_okay)
