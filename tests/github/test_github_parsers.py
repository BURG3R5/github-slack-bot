import unittest
from typing import Any

from bot.github.github_parsers import GitHubListener, convert_links, find_ref

from ..test_utils.deserializers import github_payload_deserializer
from ..test_utils.load import load_test_data
from ..test_utils.serializers import github_event_serializer


class TestMetaClass(type):

    def __new__(mcs, name: str, bases: tuple[type, ...],
                attributes: dict[str, Any]):

        def generate_test(raw_input: dict[str, Any],
                          expected_output: dict[str, Any]):

            def test_parser(self):
                event_type, raw_json = github_payload_deserializer(raw_input)
                listener = GitHubListener()

                parsed_event = listener.parse(event_type, raw_json)

                self.assertEqual(
                    github_event_serializer(parsed_event),
                    expected_output,
                )

            return test_parser

        data: dict[str, Any] = load_test_data('github')
        for method_name, (input, output) in data.items():
            attributes['test_' + method_name] = generate_test(input, output)

        return type.__new__(mcs, name, bases, attributes)


class GitHubListenerTest(unittest.TestCase, metaclass=TestMetaClass):
    # Parser tests are created dynamically by metaclass

    def test_find_ref(self):
        self.assertEqual("name", find_ref("refs/heads/name"))
        self.assertEqual("branch-name", find_ref("refs/heads/branch-name"))
        self.assertEqual("username/branch-name",
                         find_ref("refs/heads/username/branch-name"))
        self.assertEqual("branch-name", find_ref("branch-name"))

    def test_convert_links(self):
        self.assertEqual(
            "Some comment text <www.xyz.com|Link text> text",
            convert_links("Some comment text [Link text](www.xyz.com) text"))
        self.assertEqual(
            "Some comment text <www.xyz.com/abcd|Link text> text",
            convert_links(
                "Some comment text [Link text](www.xyz.com/abcd) text"))
        self.assertEqual(
            "Some comment text <www.xyz.com?q=1234|Link text> text",
            convert_links(
                "Some comment text [Link text](www.xyz.com?q=1234) text"))
        self.assertEqual(
            "Some comment text <www.xyz.com|Link text> text <https://www.qwerty.com/|Link text 2nd>",
            convert_links(
                "Some comment text [Link text](www.xyz.com) text [Link text 2nd](https://www.qwerty.com/)"
            ))
        self.assertEqual(
            "Some comment text [Link text <www.example.link.com|Link inside link text>](www.xyz.com) text",
            convert_links(
                "Some comment text [Link text [Link inside link text](www.example.link.com)](www.xyz.com) text"
            ))


if __name__ == '__main__':
    unittest.main()
