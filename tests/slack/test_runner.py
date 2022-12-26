import unittest
from unittest import skip
from unittest.mock import patch

from bottle import MultiDict

from bot.models.github import convert_keywords_to_events
from bot.models.slack import Channel
from bot.utils.log import Logger

from ..mocks.slack.runner import TestableRunner
from ..mocks.storage import MockSubscriptionStorage
from ..test_utils.comparators import Comparators
from ..test_utils.deserializers import subscriptions_deserializer
from ..test_utils.load import load_test_data


class RunnerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Fetch test data
        cls.data = load_test_data('slack')

        # Construct common Runner instance.
        cls.logger = logger = Logger(0)
        cls.secret = secret = "example_secret"
        cls.base_url = base_url = "sub.example.com"
        cls.runner = TestableRunner(logger, secret=secret, base_url=base_url)

    def setUp(self):
        # Reset subscriptions before every test
        self.runner.storage = MockSubscriptionStorage()

    @skip('This test is being skipped for the current PR')
    def test_run_calls_subscribe(self):
        raw_json = MultiDict(self.data["run|calls_subscribe"][0])
        with patch.object(self.logger, "log_command") as mock_logger:
            with patch.object(self.runner,
                              "run_subscribe_command") as mock_function:
                self.runner.run(raw_json)
        mock_function.assert_called_once_with(
            current_channel="#example-channel",
            args=["github-slack-bot", "*"],
        )
        mock_logger.assert_called_once()
        MockSubscriptionStorage.export_subscriptions.assert_called_once()

    @skip('This test is being skipped for the current PR')
    def test_run_calls_unsubscribe(self):
        raw_json = MultiDict(self.data["run|calls_unsubscribe"][0])
        with patch.object(self.logger, "log_command") as mock_logger:
            with patch.object(self.runner,
                              "run_unsubscribe_command") as mock_function:
                self.runner.run(raw_json)
        mock_function.assert_called_once_with(
            current_channel="#example-channel",
            args=["github-slack-bot", "*"],
        )
        mock_logger.assert_called_once()
        MockSubscriptionStorage.export_subscriptions.assert_called_once()

    @skip('This test is being skipped for the current PR')
    def test_run_calls_list(self):
        raw_json = MultiDict(self.data["run|calls_list"][0])
        with patch.object(self.logger, "log_command") as mock_logger:
            with patch.object(self.runner,
                              "run_list_command") as mock_function:
                self.runner.run(raw_json)
        mock_function.assert_called_once_with(
            current_channel="#example-channel")
        mock_logger.assert_not_called()

    @skip('This test is being skipped for the current PR')
    def test_run_calls_help(self):
        raw_json = MultiDict(self.data["run|calls_help"][0])
        with patch.object(self.logger, "log_command") as mock_logger:
            with patch.object(self.runner,
                              "run_help_command") as mock_function:
                self.runner.run(raw_json)
        mock_function.assert_called_once()
        mock_logger.assert_not_called()

    @skip('This test is being skipped for the current PR')
    def test_run_doesnt_call(self):
        with patch.object(self.logger, "log_command") as mock_logger:
            # Wrong command
            raw_json = MultiDict(self.data["run|doesnt_call"][0])
            self.assertIsNone(self.runner.run(raw_json))

            # No args for subscribe or unsubscribe
            raw_json = MultiDict(self.data["run|doesnt_call"][1])
            self.assertIsNone(self.runner.run(raw_json))
            raw_json = MultiDict(self.data["run|doesnt_call"][2])
            self.assertIsNone(self.runner.run(raw_json))
        mock_logger.assert_not_called()

    @skip('This test is being skipped for the current PR')
    def test_unsubscribe_single_event(self):
        response = self.runner.run_unsubscribe_command(
            "#selene",
            ["github-slack-bot", "isc"],
        )

        self.assertTrue(*Comparators.list_messages(
            self.data["run_unsubscribe_command|single_event"][1],
            response,
        ))

    @skip('This test is being skipped for the current PR')
    def test_unsubscribe_single_events(self):
        response = self.runner.run_unsubscribe_command(
            "#selene",
            ["github-slack-bot", "isc", "p"],
        )

        self.assertTrue(*Comparators.list_messages(
            self.data["run_unsubscribe_command|single_events"][1],
            response,
        ))

    @skip('This test is being skipped for the current PR')
    def test_unsubscribe_single_noargs(self):
        response = self.runner.run_unsubscribe_command(
            "#selene",
            ["github-slack-bot"],
        )

        self.assertTrue(*Comparators.list_messages(
            self.data["run_unsubscribe_command|single_noargs"][1],
            response,
        ))

    @skip('This test is being skipped for the current PR')
    def test_unsubscribe_single_all(self):
        response = self.runner.run_unsubscribe_command(
            "#selene",
            ["github-slack-bot", "*"],
        )

        self.assertTrue(*Comparators.list_messages(
            self.data["run_unsubscribe_command|single_all"][1],
            response,
        ))

    @skip('This test is being skipped for the current PR')
    def test_unsubscribe_multiple_event(self):
        self.runner.subscriptions = subscriptions_deserializer(
            self.data["run_unsubscribe_command|multiple_event"][0])

        response = self.runner.run_unsubscribe_command(
            "#selene",
            ["github-slack-bot", "isc"],
        )

        self.assertTrue(*Comparators.list_messages(
            self.data["run_unsubscribe_command|multiple_event"][1],
            response,
        ))

    @skip('This test is being skipped for the current PR')
    def test_unsubscribe_multiple_events(self):
        self.runner.subscriptions = subscriptions_deserializer(
            self.data["run_unsubscribe_command|multiple_event"][0])
        # Reuse subscriptions data

        response = self.runner.run_unsubscribe_command(
            "#selene",
            ["github-slack-bot", "isc", "p"],
        )

        self.assertTrue(*Comparators.list_messages(
            self.data["run_unsubscribe_command|multiple_events"][1],
            response,
        ))

    @skip('This test is being skipped for the current PR')
    def test_unsubscribe_multiple_noargs(self):
        self.runner.subscriptions = subscriptions_deserializer(
            self.data["run_unsubscribe_command|multiple_event"][0])
        # Reuse subscriptions data

        response = self.runner.run_unsubscribe_command(
            "#selene",
            ["github-slack-bot"],
        )

        self.assertTrue(*Comparators.list_messages(
            self.data["run_unsubscribe_command|multiple_noargs"][1],
            response,
        ))

    @skip('This test is being skipped for the current PR')
    def test_unsubscribe_multiple_all(self):
        self.runner.subscriptions = subscriptions_deserializer(
            self.data["run_unsubscribe_command|multiple_event"][0])
        # Reuse subscriptions data

        response = self.runner.run_unsubscribe_command(
            "#selene",
            ["github-slack-bot", "*"],
        )

        self.assertTrue(*Comparators.list_messages(
            self.data["run_unsubscribe_command|multiple_all"][1],
            response,
        ))

    def test_list_empty(self):
        self.runner.subscriptions = {}

        response = self.runner.run_list_command("#example-channel")

        self.assertEqual(self.data["run_list_command|empty"][1], response)

        response = self.runner.run_list_command(
            "#example-channel",
            ephemeral=True,
        )
        self.assertEqual(self.data["run_list_command|quiet"][1], response)

    @skip('This test is being skipped for the current PR')
    def test_list_default(self):
        response = self.runner.run_list_command("#selene")

        self.assertTrue(*Comparators.list_messages(
            self.data["run_list_command|default"][1], response))

    @skip('This test is being skipped for the current PR')
    def test_list_missing(self):
        response = self.runner.run_list_command("#example-channel")

        self.assertTrue(*Comparators.list_messages(
            self.data["run_list_command|missing"][1], response))

    @skip('This test is being skipped for the current PR')
    def test_list_multiple_channels(self):
        self.runner.subscriptions["example-repo"] = {
            Channel("#example-channel", convert_keywords_to_events([]))
        }

        response = self.runner.run_list_command("#example-channel")

        self.assertTrue(*Comparators.list_messages(
            self.data["run_list_command|multiple_channels"][1], response))

    @skip('This test is being skipped for the current PR')
    def test_list_multiple_repos(self):
        self.runner.subscriptions["example-repo"] = {
            Channel("#selene", convert_keywords_to_events([]))
        }

        response = self.runner.run_list_command("#selene")

        self.assertTrue(*Comparators.list_messages(
            self.data["run_list_command|multiple_repos"][1], response))

    @skip('This test is being skipped for the current PR')
    def test_list_overlapping(self):
        self.runner.subscriptions["example-repo"] = {
            Channel("#example-channel", convert_keywords_to_events([]))
        }
        self.runner.subscriptions["github-slack-bot"].add(
            Channel("#example-channel", convert_keywords_to_events(["*"])))

        response = self.runner.run_list_command("#example-channel")

        self.assertTrue(*Comparators.list_messages(
            self.data["run_list_command|overlapping"][1], response))

    @skip('This test is being skipped for the current PR')
    def test_help(self):
        response = self.runner.run_help_command([])
        self.assertEqual(self.data["run_help_command"][1], response)


if __name__ == '__main__':
    unittest.main()
