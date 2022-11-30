import json
import urllib.parse

import requests

url = "https://petite-things-join-103-37-201-146.loca.lt/slack/commands"
token = "xoxe.xoxp-1-Mi0yLTM5NDM5NTk2MzY5MTktMzk1NjA1MzE4MTM4MS00NDQxMjUwMjk2Njc0LTQ0NDE3NzkwNDc0MTAtNjM3ZWRlZmVjYTAzN2E5NjJhMTNlMzkwZWNkN2RhNDFiMmI0YTczNjE2MTFiNTM5YjExZjZhMTMyMWNlYjhjMg"
app_id = "A03UW8FPP32"


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


if __name__ == "__main__":
    update_app_manifest()
