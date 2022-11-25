# import unittest
# from enum import Enum

# from bot.models.github.event_type import EventType, convert_keywords_to_events

# class ExampleEnum(Enum):
#     BRANCH_CREATED = ("bc", "A Branch was created")
#     BRANCH_DELETED = ("bd", "A Branch was deleted")
#     TAG_CREATED = ("tc", "A Tag was created")
#     TAG_DELETED = ("td", "A Tag was deleted")
#     PULL_CLOSED = ("prc", "A Pull Request was closed")
#     PULL_MERGED = ("prm", "A Pull Request was merged")
#     PULL_OPENED = ("pro", "A Pull Request was opened")
#     PULL_READY = ("prr", "A Pull Request is ready")
#     ISSUE_OPENED = ("iso", "An Issue was opened")
#     ISSUE_CLOSED = ("isc", "An Issue was closed")
#     REVIEW = ("rv", "A Review was given on a Pull Request")
#     REVIEW_COMMENT = ("rc", "A Comment was added to a Review")
#     COMMIT_COMMENT = ("cc", "A Comment was made on a Commit")
#     ISSUE_COMMENT = ("ic", "A Comment was made on an Issue")
#     FORK = ("fk", "Repository was forked by a user")
#     PUSH = ("p", "One or more Commits were pushed")
#     RELEASE = ("rl", "A new release was published")
#     STAR_ADDED = ("sa", "A star was added to repository")
#     STAR_REMOVED = ("sr", "A star was removed from repository")

# class TestEventType(unittest.TestCase):

#     def test_convert_keywords_to_events_all_in_non_single_list(self):
#         list1 = []
#         list2 = []
#         for x in set(ExampleEnum):
#             list1.append(x)
#         for x in convert_keywords_to_events(["*"]):
#             list2.append(x)
#         self.assertEqual(list1, list2)
