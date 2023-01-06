from typing import Any


def error_message(text: str) -> dict[str, Any]:
    attachments = [
        {
            "color":
            "#bb2124",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text,
                    },
                },
            ],
        },
    ]

    return {
        "response_type": "ephemeral",
        "attachments": attachments,
    }
