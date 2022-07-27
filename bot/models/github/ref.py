"""
Model for a Git ref (branch/tag).
"""

from typing import Literal


class Ref:
    """
    Model for a Git ref (branch/tag).

    :param name: Name of the ref.
    :param ref_type: "branch" or "tag".
    """

    def __init__(
        self,
        name: str,
        ref_type: Literal["branch", "tag"] = "branch",
    ):
        self.name = name
        self.type = ref_type

    def __str__(self):
        return self.name
