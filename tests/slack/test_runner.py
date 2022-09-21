import unittest
from unittest.mock import patch

from bottle import MultiDict

from bot.models.github import convert_keywords_to_events
from bot.models.slack import Channel
from bot.slack.runner import Runner
from bot.utils.log import Logger
from bot.utils.storage import Storage

from ..test_utils.comparators import Comparators
from ..test_utils.load import load_test_data


class RunnerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Fetch test data
        cls.data = load_test_data('slack')

        # Construct common Runner instance.
        cls.logger = logger = Logger(0)
        cls.runner = Runner(logger)

    def setUp(self):
        self.runner.subscriptions = Storage.import_subscriptions()

    @patch("bot.slack.runner.Storage")
    def test_run_calls_subscribe(self, MockStorage):
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
        MockStorage.export_subscriptions.assert_called_once()

    @patch("bot.slack.runner.Storage")
    def test_run_calls_unsubscribe(self, MockStorage):
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
        MockStorage.export_subscriptions.assert_called_once()

    @patch("bot.slack.runner.Storage")
    def test_run_calls_list(self, _):
        raw_json = MultiDict(self.data["run|calls_list"][0])
        with patch.object(self.logger, "log_command") as mock_logger:
            with patch.object(self.runner,
                              "run_list_command") as mock_function:
                self.runner.run(raw_json)
        mock_function.assert_called_once_with(
            current_channel="#example-channel")
        mock_logger.assert_not_called()

    @patch("bot.slack.runner.Storage")
    def test_run_calls_help(self, _):
        raw_json = MultiDict(self.data["run|calls_help"][0])
        with patch.object(self.logger, "log_command") as mock_logger:
            with patch.object(self.runner,
                              "run_help_command") as mock_function:
                self.runner.run(raw_json)
        mock_function.assert_called_once()
        mock_logger.assert_not_called()

    @patch("bot.slack.runner.Storage")
    def test_run_doesnt_call(self, _):
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

    def test_list_empty(self):
        self.runner.subscriptions = {}

        response = self.runner.run_list_command("#example-channel")

        self.assertEqual(self.data["run_list_command|empty"][1], response)

    def test_list_default(self):
        response = self.runner.run_list_command("#github-slack-bot")

        self.assertTrue(*Comparators.list_messages(
            self.data["run_list_command|default"][1], response))

    def test_list_missing(self):
        response = self.runner.run_list_command("#example-channel")

        self.assertTrue(*Comparators.list_messages(
            self.data["run_list_command|missing"][1], response))

    def test_list_multiple_channels(self):
        self.runner.subscriptions["example-repo"] = {
            Channel("#example-channel", convert_keywords_to_events([]))
        }

        response = self.runner.run_list_command("#example-channel")

        self.assertTrue(*Comparators.list_messages(
            self.data["run_list_command|multiple_channels"][1], response))

    def test_list_multiple_repos(self):
        self.runner.subscriptions["example-repo"] = {
            Channel("#github-slack-bot", convert_keywords_to_events([]))
        }

        response = self.runner.run_list_command("#github-slack-bot")

        self.assertTrue(*Comparators.list_messages(
            self.data["run_list_command|multiple_repos"][1], response))

    def test_list_overlapping(self):
        self.runner.subscriptions["example-repo"] = {
            Channel("#example-channel", convert_keywords_to_events([]))
        }
        self.runner.subscriptions["github-slack-bot"].add(
            Channel("#example-channel", convert_keywords_to_events(["*"])))

        response = self.runner.run_list_command("#example-channel")

        self.assertTrue(*Comparators.list_messages(
            self.data["run_list_command|overlapping"][1], response))

    def test_help(self):
        response = self.runner.run_help_command()

        self.assertEqual(self.data["run_help_command"][1], response)


if __name__ == '__main__':
    unittest.main()
