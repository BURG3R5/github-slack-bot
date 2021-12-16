from abc import ABC, abstractmethod

from models.event_type import EventType
from models.github_event import GitHubEvent
from utils.json_utils import JSON


class GitHubPayloadParser:
    @staticmethod
    def parse(raw_json) -> GitHubEvent:
        json: JSON = JSON(raw_json)
        event_parsers: list = [
            BranchEventParser,
            IssueOpenEventParser,
            IssueCloseEventParser,
            PullOpenEventParser,
            PullReadyEventParser,
            PushEventParser,
            ReviewEventParser,
        ]
        for event_parser in event_parsers:
            if event_parser.verify_payload(json):
                return event_parser.cast_payload_to_event(json)


# Helper classes:


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
        return (
            "ref_type" in json
            and json["ref_type"] == "branch"
            and json["pusher_type"] == "user"
        )

    @staticmethod
    def cast_payload_to_event(json: JSON) -> GitHubEvent:
        return GitHubEvent(
            # TODO: Classify branch events into created and deleted.
            event_type=EventType.branch_created,
            repo=json["repository"]["name"],
            user=json["sender"][("name", "login")],
            branch=json["ref"].split("/")[-1],
        )


class IssueOpenEventParser(EventParser):
    @staticmethod
    def verify_payload(json: JSON) -> bool:
        return ("issue" in json) and (json["action"] == "opened")

    @staticmethod
    def cast_payload_to_event(json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.issue_opened,
            repo=json["repository"]["name"],
            user=json["issue"]["user"]["login"],
            number=json["issue"]["number"],
            title=json["issue"]["title"],
        )


class IssueCloseEventParser(EventParser):
    @staticmethod
    def verify_payload(json: JSON) -> bool:
        return ("issue" in json) and (json["action"] == "closed")

    @staticmethod
    def cast_payload_to_event(json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.issue_closed,
            repo=json["repository"]["name"],
            user=json["issue"]["user"]["login"],
            number=json["issue"]["number"],
            title=json["issue"]["title"],
        )


class PullOpenEventParser(EventParser):
    @staticmethod
    def verify_payload(json: JSON) -> bool:
        return ("pull_request" in json) and (json["action"] == "opened")

    @staticmethod
    def cast_payload_to_event(json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.pull_opened,
            repo=json["repository"]["name"],
            number=json["number"],
            title=json["pull_request"]["title"],
            user=json["pull_request"]["user"]["login"],
        )


class PullReadyEventParser(EventParser):
    @staticmethod
    def verify_payload(json: JSON) -> bool:
        return ("pull_request" in json) and (json["action"] == "review_requested")

    @staticmethod
    def cast_payload_to_event(json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.pull_ready,
            repo=json["repository"]["name"],
            number=json["number"],
            title=json["pull_request"]["title"],
            reviewers=[user["login"] for user in json["requested_reviewers"]],
        )


class PushEventParser(EventParser):
    @staticmethod
    def verify_payload(json: JSON) -> bool:
        return ("commits" in json) and (len(json["commits"]) > 0)

    @staticmethod
    def cast_payload_to_event(json: JSON) -> GitHubEvent:
        base_url = json["repository"]["html_url"]
        username = json[("pusher", "sender")][("name", "login")]
        branch_name = json["ref"].split("/")[-1]

        # Commits
        commits: list[str] = []
        for commit in json["commits"]:
            sha = commit["id"]
            commit_link = base_url + f"/commit/{sha}"
            commits.append(f"`<{commit_link}|{sha[:8]}>` - " f'*{commit["message"]}*')

        return GitHubEvent(
            event_type=EventType.push,
            repo=json["repository"]["name"],
            number_of_commits=len(commits),
            branch=f"`<{base_url}/tree/{branch_name}|{branch_name}>`",
            user=f"<https://github.com/{username}|{username}>",
            commits=commits,
        )


class ReviewEventParser(EventParser):
    @staticmethod
    def verify_payload(json: JSON) -> bool:
        return (
            ("review" in json)
            and (json["action"] == "submitted")
            and (json["review"]["state"].lower() in ["approved", "changes_requested"])
        )

    @staticmethod
    def cast_payload_to_event(json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.review,
            repo=json["repository"]["name"],
            number=json["pull_request"]["number"],
            status=json["review"]["state"].lower(),
            reviewers=[json["review"]["user"]["login"]],
        )
