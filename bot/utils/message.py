class write_message:

    def give_ephemral_reply(self, statement: str) -> dict[str, Any]:
        return {
            "response_type":
            "ephemeral",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (f"{statement}"),
                    },
                },
            ]
        }
