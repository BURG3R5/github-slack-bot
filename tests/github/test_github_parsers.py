import unittest

from bot.github.github_parsers import GitHubPayloadParser, find_ref

from ..utils.deserializers import github_payload_deserializer
from ..utils.load import load_test_data
from ..utils.serializers import github_event_serializer


class GitHubPayloadParserTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.data = load_test_data('github')

    def test_parsers(self):
        for testcase, (raw_input, expected_output) in self.data.items():
            event_type, raw_json = github_payload_deserializer(raw_input)

            output = GitHubPayloadParser.parse(event_type, raw_json)

            self.assertEqual(github_event_serializer(output), expected_output,
                             f"Test case labeled `{testcase}` failed.")

    def test_find_ref(self):
        self.assertEqual("name", find_ref("refs/heads/name"))
        self.assertEqual("branch-name", find_ref("refs/heads/branch-name"))
        self.assertEqual("username/branch-name",
                         find_ref("refs/heads/username/branch-name"))
        self.assertEqual("branch-name", find_ref("branch-name"))


if __name__ == '__main__':
    unittest.main()
