import unittest

from bot.models.github.pull_request import PullRequest


class PullRequestTest(unittest.TestCase):

    def test_should_create_pull_request(self):
        pr = PullRequest("hey, this is Unittest pr", "44",
                         "www.unittestpr.com")
        self.assertEqual(str(pr),
                         "<www.unittestpr.com|#44 hey, this is Unittest pr>")
