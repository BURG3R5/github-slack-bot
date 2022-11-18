import re
from typing import Any


def extract_letter_sequences(string: str) -> list[str]:
    letter_sequence_regexp = re.compile(r'[\w\-_]+')
    return sorted(letter_sequence_regexp.findall(string.lower()))


class Comparators:

    @staticmethod
    def list_messages(message_1: dict[str, Any],
                      message_2: dict[str, Any]) -> tuple[bool, str]:
        try:
            if message_1["response_type"] != message_2["response_type"]:
                return False, "response type differs"
            if len(message_1["blocks"]) != len(message_2["blocks"]):
                return False, f"different number of blocks {len(message_1['blocks'])} vs {len(message_2['blocks'])}"

            for block_1, block_2 in zip(message_1["blocks"],
                                        message_2["blocks"]):
                if block_1["type"] != block_2["type"]:
                    return False, "block type differs"
                if block_1["type"] == "section":
                    sub_block_1, sub_block_2 = block_1["text"], block_2["text"]
                    if sub_block_1["type"] != sub_block_2["type"]:
                        return False, "sub-block type differs"
                    if extract_letter_sequences(
                            sub_block_1["text"]) != extract_letter_sequences(
                                sub_block_2["text"]):
                        return False, f"content differs {sub_block_1['text']} vs {sub_block_2['text']}"
        except KeyError:
            # If anything is missing
            return False, "missing key"

        # If everything's alright
        return True, ""
