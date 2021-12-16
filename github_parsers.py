from abc import ABC, abstractmethod

from models.github import Commit, EventType, GitHubEvent, Ref, User, Repository
from models.slack import Link
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
            TagEventParser,
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
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["sender"][("name", "login")]),
            branch=Ref(name=json["ref"].split("/")[-1]),
        )


class CommitCommentEventParser(EventParser):
    @staticmethod
    def verify_payload(json: JSON) -> bool:
        return "comment" in json and json["action"] == "created"

    @staticmethod
    def cast_payload_to_event(json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.commit_comment,
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["comment"]["user"]["login"]),
            comments=[json["comment"]["body"]],
            commits=[Commit(sha=json["comment"]["commit_id"][:8])],
            links=[Link(url=json["comment"]["html_url"])],
        )


class IssueOpenEventParser(EventParser):
    @staticmethod
    def verify_payload(json: JSON) -> bool:
        return ("issue" in json) and (json["action"] == "opened")

    @staticmethod
    def cast_payload_to_event(json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.issue_opened,
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["issue"]["user"]["login"]),
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
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["issue"]["user"]["login"]),
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
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["pull_request"]["user"]["login"]),
            number=json["number"],
            title=json["pull_request"]["title"],
        )


class PullReadyEventParser(EventParser):
    @staticmethod
    def verify_payload(json: JSON) -> bool:
        return ("pull_request" in json) and (json["action"] == "review_requested")

    @staticmethod
    def cast_payload_to_event(json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.pull_ready,
            repo=Repository(name=json["repository"]["name"]),
            number=json["number"],
            title=json["pull_request"]["title"],
            reviewers=[
                User(name=user["login"]) for user in json["requested_reviewers"]
            ],
        )


class PushEventParser(EventParser):
    @staticmethod
    def verify_payload(json: JSON) -> bool:
        return ("commits" in json) and (len(json["commits"]) > 0)

    @staticmethod
    def cast_payload_to_event(json: JSON) -> GitHubEvent:
        base_url = json["repository"]["html_url"]
        branch_name = json["ref"].split("/")[-1]

        # Commits
        commits: list[Commit] = []
        for commit in json["commits"]:
            commits.append(
                Commit(
                    message=commit["message"],
                    sha=commit["id"],
                    link=base_url + f"/commit/{commit['id']}",
                )
            )

        return GitHubEvent(
            event_type=EventType.push,
            repo=Repository(name=json["repository"]["name"], link=base_url),
            branch=Ref(name=branch_name, link=f"{base_url}/tree/{branch_name}"),
            user=User(name=json[("pusher", "sender")][("name", "login")]),
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
            repo=Repository(name=json["repository"]["name"]),
            number=json["pull_request"]["number"],
            status=json["review"]["state"].lower(),
            reviewers=[User(name=json["review"]["user"]["login"])],
        )


class TagEventParser(EventParser):
    @staticmethod
    def verify_payload(json: JSON) -> bool:
        return (
            "ref_type" in json
            and json["ref_type"] == "tag"
            and json["pusher_type"] == "user"
        )

    @staticmethod
    def cast_payload_to_event(json: JSON) -> GitHubEvent:
        return GitHubEvent(
            # TODO: Classify tag events into created and deleted.
            event_type=EventType.tag_created,
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["sender"][("name", "login")]),
            branch=Ref(name=json["ref"].split("/")[-1], ref_type="tag"),
        )
