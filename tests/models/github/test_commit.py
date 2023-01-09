import unittest

from bot.models.github.commit import Commit


class CommitTest(unittest.TestCase):

    def test_should_create_commit(self):
        commit = Commit(message="Hello, this is unittest",
                        sha="0009829KJHB998SB",
                        link="www.unittest.com")
        self.assertEqual(str(commit),
                         "<Hello, this is unittest|www.unittest.com>")
