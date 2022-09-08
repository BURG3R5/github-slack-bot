from typing import Any


def github_payload_deserializer(json: dict[str, Any]):
    return json["event_type"], json["raw_json"]
