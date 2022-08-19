import unittest
from typing import Any

from bot.github.github_parsers import GitHubPayloadParser, find_ref

from ..utils.deserializers import github_payload_deserializer
from ..utils.load import load_test_data
from ..utils.serializers import github_event_serializer


class TestMetaClass(type):

    def __new__(mcs, name: str, bases: tuple[type, ...],
                attributes: dict[str, Any]):

        def generate_test(raw_input: dict[str, Any],
                          expected_output: dict[str, Any]):

            def test_parser(self):
                event_type, raw_json = github_payload_deserializer(raw_input)

                parsed_event = GitHubPayloadParser.parse(event_type, raw_json)

                self.assertEqual(
                    github_event_serializer(parsed_event),
                    expected_output,
                )

            return test_parser

        data: dict[str, Any] = load_test_data('github')
        for method_name, (input, output) in data.items():
            attributes['test_' + method_name] = generate_test(input, output)

        return type.__new__(mcs, name, bases, attributes)


class GitHubPayloadParserTest(unittest.TestCase, metaclass=TestMetaClass):
    # Parser tests are created dynamically by metaclass

    def test_find_ref(self):
        self.assertEqual("name", find_ref("refs/heads/name"))
        self.assertEqual("branch-name", find_ref("refs/heads/branch-name"))
        self.assertEqual("username/branch-name",
                         find_ref("refs/heads/username/branch-name"))
        self.assertEqual("branch-name", find_ref("branch-name"))


if __name__ == '__main__':
    unittest.main()
