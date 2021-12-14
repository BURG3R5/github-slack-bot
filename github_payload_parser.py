from abc import ABC, abstractmethod

from models.github_event import GitHubEvent
from utils.json_utils import JSON


class GitHubPayloadParser:
    @staticmethod
    def parse(raw_json) -> GitHubEvent:
        json: JSON = JSON(raw_json)
        event_parsers: list = [BranchEventParser, IssueEventParser]
        for event_parser in event_parsers:
            if event_parser.verify_payload(json):
                return event_parser.case_payload_to_event(json)


class EventParser(ABC):
    @staticmethod
    @abstractmethod
    def verify_payload(json: JSON) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def cast_payload_to_event(json: JSON) -> GitHubEvent:
        pass


class BranchEventParser(EventParser):
    @staticmethod
    def verify_payload(json: JSON) -> bool:
        return 'ref_type' in json and \
               json['ref_type'] == 'branch' and \
               json['pusher_type'] == 'user'

    @staticmethod
    def cast_payload_to_event(json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type='branch',
            repo=json['repository']['name'],
            user=json['sender'][('name', 'login')],
            branch=json['ref'].split('/')[-1],
        )


class IssueEventParser(EventParser):
    @staticmethod
    def verify_payload(json: JSON) -> bool:
        return ('issue' in json) and \
               (json['action'] == 'opened')

    @staticmethod
    def cast_payload_to_event(json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type='issue',
            repo=json['repository']['name'],
            user=json['issue']['user']['login'],
            number=json['issue']['number'],
            title=json['issue']['title'],
        )

# TODO: Add other parsers.
