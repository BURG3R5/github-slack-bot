from abc import ABC, abstractmethod
from typing import Type

from models.github import Commit, EventType, GitHubEvent, Ref, User, Repository
from models.link import Link
from utils import JSON


class GitHubPayloadParser:
    @staticmethod
    def parse(event_type, raw_json) -> GitHubEvent | None:
        json: JSON = JSON(raw_json)
        event_parsers: list[Type[EventParser]] = [
            BranchCreateEventParser,
            BranchDeleteEventParser,
            CommitCommentEventParser,
            ForkEventParser,
            IssueOpenEventParser,
            IssueCloseEventParser,
            IssueCommentEventParser,
            PullCloseEventParser,
            PullMergeEventParser,
            PullOpenEventParser,
            PullReadyEventParser,
            PushEventParser,
            ReleaseEventParser,
            ReviewEventParser,
            ReviewCommentEventParser,
            StarAddEventParser,
            StarRemoveEventParser,
            TagCreateEventParser,
            TagDeleteEventParser,
        ]
        for event_parser in event_parsers:
            if event_parser.verify_payload(event_type=event_type, json=json):
                return event_parser.cast_payload_to_event(
                    event_type=event_type,
                    json=json,
                )
        print(f"Undefined event: {raw_json}")
        return None


# Helper classes:


class EventParser(ABC):
    @staticmethod
    @abstractmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        pass


class BranchCreateEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (
            event_type == "create"
            and json["ref_type"] == "branch"
            and json["pusher_type"] == "user"
        )

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.branch_created,
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["sender"][("name", "login")]),
            branch=Ref(name=json["ref"].split("/")[-1]),
        )


class BranchDeleteEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (
            event_type == "delete"
            and json["ref_type"] == "branch"
            and json["pusher_type"] == "user"
        )

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.branch_deleted,
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["sender"][("name", "login")]),
            branch=Ref(name=json["ref"].split("/")[-1]),
        )


class CommitCommentEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "commit_comment") and (json["action"] == "created")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.commit_comment,
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["comment"]["user"]["login"]),
            comments=[json["comment"]["body"]],
            commits=[Commit(sha=json["comment"]["commit_id"][:8])],
            links=[Link(url=json["comment"]["html_url"])],
        )


class ForkEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return event_type == "fork"

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.fork,
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["forkee"]["owner"]["login"]),
            links=[json["forkee"]["html_url"]],
        )


class IssueOpenEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "issues") and (json["action"] == "opened")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.issue_opened,
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["issue"]["user"]["login"]),
            number=json["issue"]["number"],
            title=json["issue"]["title"],
        )


class IssueCloseEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "issues") and (json["action"] == "closed")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.issue_closed,
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["issue"]["user"]["login"]),
            number=json["issue"]["number"],
            title=json["issue"]["title"],
        )


class IssueCommentEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "issue_comment") and (json["action"] == "created")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.issue_comment,
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["sender"]["login"]),
            number=json["issue"]["number"],
            title=json["issue"]["title"],
            comments=[json["body"]],
        )


class PullCloseEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (
            (event_type == "pull_request")
            and (json["action"] == "closed")
            and (not json["pull_request"]["merged"])
        )

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.pull_closed,
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["pull_request"]["user"]["login"]),
            number=json["number"],
            title=json["pull_request"]["title"],
        )


class PullMergeEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (
            (event_type == "pull_request")
            and (json["action"] == "closed")
            and (json["pull_request"]["merged"])
        )

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.pull_merged,
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["pull_request"]["user"]["login"]),
            number=json["number"],
            title=json["pull_request"]["title"],
        )


class PullOpenEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "pull_request") and (json["action"] == "opened")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.pull_opened,
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["pull_request"]["user"]["login"]),
            number=json["number"],
            title=json["pull_request"]["title"],
        )


class PullReadyEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "pull_request") and (json["action"] == "review_requested")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.pull_ready,
            repo=Repository(name=json["repository"]["name"]),
            number=json["number"],
            title=json["pull_request"]["title"],
            reviewers=[
                User(name=user["login"])
                for user in json["pull_request"]["requested_reviewers"]
            ],
        )


class PushEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "push") and (len(json["commits"]) > 0)

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        base_url = json["repository"]["html_url"]
        branch_name = json["ref"].split("/")[-1]

        # Commits
        commits: list[Commit] = [
            Commit(
                message=commit["message"],
                sha=commit["id"],
                link=base_url + f"/commit/{commit['id']}",
            )
            for commit in json["commits"]
        ]

        return GitHubEvent(
            event_type=EventType.push,
            repo=Repository(name=json["repository"]["name"], link=base_url),
            branch=Ref(name=branch_name, link=f"{base_url}/tree/{branch_name}"),
            user=User(name=json[("pusher", "sender")][("name", "login")]),
            commits=commits,
        )


class ReleaseEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "release") and (json["action"] == "released")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.release,
            repo=Repository(name=json["repository"]["name"]),
            status=json["action"],
            title=json["tag_name"],
        )


class ReviewEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (
            (event_type == "pull_request_review")
            and (json["action"] == "submitted")
            and (json["review"]["state"].lower() in ["approved", "changes_requested"])
        )

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.review,
            repo=Repository(name=json["repository"]["name"]),
            number=json["pull_request"]["number"],
            status=json["review"]["state"].lower(),
            reviewers=[User(name=json["review"]["user"]["login"])],
        )


class ReviewCommentEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (
            (event_type == "pull_request_review_comment")
            and (json["action"] == "created")
            and (json["review"]["state"].lower() in ["approved", "changes_requested"])
        )

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.review_comment,
            repo=Repository(name=json["repository"]["name"]),
            number=json["pull_request"]["number"],
            links=[Link(url=json["comment"]["url"])],
            reviewers=[User(name=json["review"]["user"]["login"])],
        )


class StarAddEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "star") and (json["action"] == "created")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.star_added,
            repo=Repository(name=json["repository"]["name"]),
        )


class StarRemoveEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "star") and (json["action"] == "deleted")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.star_removed,
            repo=Repository(name=json["repository"]["name"]),
        )


class TagCreateEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (
            event_type == "create"
            and json["ref_type"] == "tag"
            and json["pusher_type"] == "user"
        )

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.tag_created,
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["sender"][("name", "login")]),
            branch=Ref(name=json["ref"].split("/")[-1], ref_type="tag"),
        )


class TagDeleteEventParser(EventParser):
    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (
            event_type == "delete"
            and json["ref_type"] == "tag"
            and json["pusher_type"] == "user"
        )

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.tag_deleted,
            repo=Repository(name=json["repository"]["name"]),
            user=User(name=json["sender"][("name", "login")]),
            branch=Ref(name=json["ref"].split("/")[-1], ref_type="tag"),
        )
