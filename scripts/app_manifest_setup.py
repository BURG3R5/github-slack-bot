"""
Steps:
1) Go to https://api.slack.com/authentication/config-tokens#creating
2) Create App config tokens
3) Paste your tokens and url in ../.env
4) Run this script

"""

import json
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


def update_app_manifest() -> tuple[int, bool]:
    prev_manifest = get_prev_manifest()

    for i in range(4):
        prev_manifest["features"]["slash_commands"][i].update({"url": url})

    endpoint = "https://slack.com/api/apps.manifest.update/"
    response = requests.post(
        endpoint,
        params={
            "app_id": app_id,
            "manifest": json.dumps(prev_manifest),
        },
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    return response.status_code, response.json()["ok"]


def get_prev_manifest() -> dict[str, Any]:
    endpoint = f"https://slack.com/api/apps.manifest.export/"
    response = requests.post(
        endpoint,
        params={
            "app_id": app_id
        },
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
    ).json()

    if response["ok"]:
        return response["manifest"]
    else:
        print(response)
        raise Exception()


def rotate_token() -> tuple[str, str]:
    endpoint = "https://slack.com/api/tooling.tokens.rotate/"
    response = requests.post(
        endpoint,
        params={
            "refresh_token": refresh_token
        },
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    ).json()
    if response["ok"]:
        return response["token"], response["refresh_token"]
    else:
        print(response)
        raise Exception()


if __name__ == "__main__":
    load_dotenv(Path("..") / ".env")

    app_id = os.environ["SLACK_APP_ID"]
    refresh_token = os.environ["MANIFEST_REFRESH_TOKEN"]
    token = os.environ["MANIFEST_ACCESS_TOKEN"]
    url = os.environ["BASE_URL"] + "/slack/commands"
    if not url.startswith("https://"):
        url = "https://" + url

    token, refresh_token = rotate_token()
    status_code, is_okay = update_app_manifest()
    print(status_code, is_okay)
