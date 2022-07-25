"""
Contains the `JSON` class, which wraps a `dict` to safely extract values using multiple keys.
"""

from typing import Any

from bottle import MultiDict


class JSON:
    """
    Wrapper for a `dict`. Safely extracts values using multiple keys.

    :param dictionary: A normal `dict` object.
    """

    def __contains__(self, key) -> bool:
        return key in self.data

    def __init__(self, dictionary: dict) -> None:
        self.data = dictionary

    def __getitem__(self, keys) -> Any:
        def get(k):
            if isinstance(self.data[k], dict):
                return JSON(self.data[k])
            return self.data[k]

        # Single key
        if isinstance(keys, str):
            key = keys
            if key in self.data:
                return get(key)
            return key.upper()
        # Multiple keys
        for key in keys:
            if key in self.data:
                return get(key)
        return keys[0].upper()

    @staticmethod
    def from_multi_dict(multi_dict: MultiDict):
        """
        Converts `bottle.MultiDict` to `JSON`.
        :param multi_dict: Incoming `MultiDict`.
        :return: `JSON` object containing the data from the `MultiDict`.
        """
        return JSON({key: multi_dict[key] for key in multi_dict.keys()})
