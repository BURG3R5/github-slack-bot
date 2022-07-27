"""
Collection of models related to the GitHub portion of the project.
"""

# Import all trivial models
from .commit import Commit
from .event_type import EventType, convert_keywords_to_events
from .issue import Issue
from .pull_request import PullRequest
from .ref import Ref
from .repository import Repository
from .user import User
