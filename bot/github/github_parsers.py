"""
Contains the `GitHubPayloadParser` and `*EventParser` classes, to handle parsing of webhook data.

Exposed API is only the `GitHubPayloadParser.parse` function, to serialize the raw event data.
"""

import re
from abc import ABC, abstractmethod
from typing import Type

from ..models.github import Commit, EventType, Issue, PullRequest, Ref, Repository, User
from ..models.github.event import GitHubEvent
from ..models.link import Link
from ..utils.json import JSON


class GitHubPayloadParser:
    """
    Wrapper for a single method (`parse`), for consistency's sake only.
    """

    @staticmethod
    def parse(event_type, raw_json) -> GitHubEvent | None:
        """
        Checks the data against all parsers, then returns a `GitHubEvent` using the matching parser.
        :param event_type: Event type header received from GitHub.
        :param raw_json: Event data body received from GitHub.
        :return: `GitHubEvent` object containing all the relevant data about the event.
        """
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
        print(f"Undefined event: {event_type}\n***\n{raw_json}***")
        return None


# Helper classes:
class EventParser(ABC):
    """
    Abstract base class for all parsers, to enforce them to implement check and cast methods.
    """

    @staticmethod
    @abstractmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        """
        Verifies whether the passed event data is of the parser's type.
        :param event_type: Event type header received from GitHub.
        :param json: Event data body received from GitHub.
        :return: Whether the event is of the parser's type.
        """

    @staticmethod
    @abstractmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        """
        Extracts all the important data from the passed raw data, and returns it in a `GitHubEvent`.
        :param event_type: Event type header received from GitHub.
        :param json: Event data body received from GitHub.
        :return: `GitHubEvent` object containing all the relevant data about the event.
        """


class BranchCreateEventParser(EventParser):
    """
    Parser for branch creation events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "create" and json["ref_type"] == "branch"
                and json["pusher_type"] == "user")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.BRANCH_CREATED,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            user=User(name=json["sender"][("name", "login")]),
            ref=Ref(name=find_ref(json["ref"])),
        )


class BranchDeleteEventParser(EventParser):
    """
    Parser for branch deletion events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "delete" and json["ref_type"] == "branch"
                and json["pusher_type"] == "user")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.BRANCH_DELETED,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            user=User(name=json["sender"][("name", "login")]),
            ref=Ref(name=find_ref(json["ref"])),
        )


class CommitCommentEventParser(EventParser):
    """
    Parser for comments on commits.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return event_type == "commit_comment" and json["action"] == "created"

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.COMMIT_COMMENT,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            user=User(name=json["comment"]["user"]["login"]),
            comments=[convert_links(json["comment"]["body"])],
            commits=[
                Commit(
                    sha=json["comment"]["commit_id"][:8],
                    link=json["repository"]["html_url"] + "/commit/" +
                    json["comment"]["commit_id"][:8],
                    message="",
                )
            ],
            links=[Link(url=json["comment"]["html_url"])],
        )


class ForkEventParser(EventParser):
    """
    Parser for repository fork events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return event_type == "fork"

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.FORK,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            user=User(name=json["forkee"]["owner"]["login"]),
            links=[Link(url=json["forkee"]["html_url"])],
        )


class IssueOpenEventParser(EventParser):
    """
    Parser for issue creation events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "issues") and (json["action"] == "opened")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.ISSUE_OPENED,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            user=User(name=json["issue"]["user"]["login"]),
            issue=Issue(
                number=json["issue"]["number"],
                title=json["issue"]["title"],
                link=json["issue"]["html_url"],
            ),
        )


class IssueCloseEventParser(EventParser):
    """
    Parser for issue closing events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "issues") and (json["action"] == "closed")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.ISSUE_CLOSED,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            user=User(name=json["issue"]["user"]["login"]),
            issue=Issue(
                number=json["issue"]["number"],
                title=json["issue"]["title"],
                link=json["issue"]["html_url"],
            ),
        )


class IssueCommentEventParser(EventParser):
    """
    Parser for comments on issues.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return event_type == "issue_comment" and json["action"] == "created"

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.ISSUE_COMMENT,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            user=User(name=json["sender"]["login"]),
            issue=Issue(
                number=json["issue"]["number"],
                title=json["issue"]["title"],
                link=json["issue"]["html_url"],
            ),
            comments=[convert_links(json["comment"]["body"])],
            links=[Link(url=json["comment"]["html_url"])],
        )


class PingEventParser(EventParser):
    """
    Parser for GitHub's testing ping events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return event_type == "ping"

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON):
        print("Ping event received!")


class PullCloseEventParser(EventParser):
    """
    Parser for PR closing events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return ((event_type == "pull_request") and (json["action"] == "closed")
                and (not json["pull_request"]["merged"]))

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.PULL_CLOSED,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            user=User(name=json["pull_request"]["user"]["login"]),
            pull_request=PullRequest(
                number=json["pull_request"]["number"],
                title=json["pull_request"]["title"],
                link=json["pull_request"]["html_url"],
            ),
        )


class PullMergeEventParser(EventParser):
    """
    Parser for PR merging events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return ((event_type == "pull_request") and (json["action"] == "closed")
                and (json["pull_request"]["merged"]))

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.PULL_MERGED,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            user=User(name=json["pull_request"]["user"]["login"]),
            pull_request=PullRequest(
                number=json["pull_request"]["number"],
                title=json["pull_request"]["title"],
                link=json["pull_request"]["html_url"],
            ),
        )


class PullOpenEventParser(EventParser):
    """
    Parser for PR creation events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "pull_request") and (json["action"] == "opened")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.PULL_OPENED,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            user=User(name=json["pull_request"]["user"]["login"]),
            pull_request=PullRequest(
                number=json["pull_request"]["number"],
                title=json["pull_request"]["title"],
                link=json["pull_request"]["html_url"],
            ),
        )


class PullReadyEventParser(EventParser):
    """
    Parser for PR review request events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "pull_request"
                and json["action"] == "review_requested")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.PULL_READY,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            pull_request=PullRequest(
                number=json["pull_request"]["number"],
                title=json["pull_request"]["title"],
                link=json["pull_request"]["html_url"],
            ),
            reviewers=[
                User(name=user["login"])
                for user in json["pull_request"]["requested_reviewers"]
            ],
        )


class PushEventParser(EventParser):
    """
    Parser for code push events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "push") and (len(json["commits"]) > 0)

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        base_url = json["repository"]["html_url"]
        branch_name = find_ref(json["ref"])

        # Commits
        commits: list[Commit] = [
            Commit(
                message=commit["message"],
                sha=commit["id"][:8],
                link=base_url + f"/commit/{commit['id']}",
            ) for commit in json["commits"]
        ]

        return GitHubEvent(
            event_type=EventType.PUSH,
            repo=Repository(name=json["repository"]["full_name"],
                            link=base_url),
            ref=Ref(name=branch_name),
            user=User(name=json[("pusher", "sender")][("name", "login")]),
            commits=commits,
        )


class ReleaseEventParser(EventParser):
    """
    Parser for release creation events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "release") and (json["action"] == "released")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.RELEASE,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            status="created" if json["action"] == "released" else "",
            ref=Ref(
                name=json["release"]["tag_name"],
                ref_type="tag",
            ),
            user=User(name=json["sender"]["login"]),
        )


class ReviewEventParser(EventParser):
    """
    Parser for PR review events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "pull_request_review"
                and json["action"] == "submitted"
                and json["review"]["state"].lower()
                in ["approved", "changes_requested"])

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.REVIEW,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            pull_request=PullRequest(
                number=json["pull_request"]["number"],
                title=json["pull_request"]["title"],
                link=json["pull_request"]["html_url"],
            ),
            status=json["review"]["state"].lower(),
            reviewers=[User(name=json["sender"]["login"])],
        )


class ReviewCommentEventParser(EventParser):
    """
    Parser for comments added to PR review.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "pull_request_review_comment"
                and json["action"] == "created")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.REVIEW_COMMENT,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            user=User(name=json["sender"]["login"]),
            pull_request=PullRequest(
                number=json["pull_request"]["number"],
                title=json["pull_request"]["title"],
                link=json["pull_request"]["html_url"],
            ),
            comments=[convert_links(json["comment"]["body"])],
            links=[Link(url=json["comment"]["html_url"])],
        )


class StarAddEventParser(EventParser):
    """
    Parser for repository starring events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "star") and (json["action"] == "created")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.STAR_ADDED,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            user=User(name=json["sender"]["login"]),
        )


class StarRemoveEventParser(EventParser):
    """
    Parser for repository unstarring events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "star") and (json["action"] == "deleted")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.STAR_REMOVED,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            user=User(name=json["sender"]["login"]),
        )


class TagCreateEventParser(EventParser):
    """
    Parser for tag creation events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "create" and json["ref_type"] == "tag"
                and json["pusher_type"] == "user")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.TAG_CREATED,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            user=User(name=json["sender"][("name", "login")]),
            ref=Ref(name=find_ref(json["ref"]), ref_type="tag"),
        )


class TagDeleteEventParser(EventParser):
    """
    Parser for tag deletion events.
    """

    @staticmethod
    def verify_payload(event_type: str, json: JSON) -> bool:
        return (event_type == "delete" and json["ref_type"] == "tag"
                and json["pusher_type"] == "user")

    @staticmethod
    def cast_payload_to_event(event_type: str, json: JSON) -> GitHubEvent:
        return GitHubEvent(
            event_type=EventType.TAG_DELETED,
            repo=Repository(
                name=json["repository"]["full_name"],
                link=json["repository"]["html_url"],
            ),
            user=User(name=json["sender"][("name", "login")]),
            ref=Ref(
                name=find_ref(json["ref"]),
                ref_type="tag",
            ),
        )


# Helper functions:
def find_ref(x: str) -> str:
    """
    Helper function to extract branch name
    :param x: Full version of ref id.
    :return: Extracted ref name.
    """
    return x[x.find("/", x.find("/") + 1) + 1:]


def convert_links(x: str) -> str:
    """
    Helper function to format links from Github format to Slack format
    :param x: Raw Github text.
    :return: Formatted text.
    """
    reg: str = r'\[([a-zA-Z0-9!@#$%^&*,./?\'";:_=~` ]+)\]\(([(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b[-a-zA-Z0-9@:%_\+.~#?&//=]*)\)'
    gh_links: list[tuple[str, str]] = re.findall(reg, x)
    for (txt, link) in gh_links:
        old: str = f"[{txt}]({link})"
        txt = str(txt).strip()
        link = str(link).strip()
        new: str = f"<{link}|{txt}>"
        x = x.replace(old, new)
    return x
