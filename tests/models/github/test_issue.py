import unittest

from bot.models.github.issue import Issue


class IssueTest(unittest.TestCase):

    def test_should_create_issue(self):
        issue = Issue(title="unittest issue",
                      number="22",
                      link="www.unittestIsue.com")
        self.assertEqual(str(issue),
                         "<www.unittestIsue.com|#22 unittest issue>")
