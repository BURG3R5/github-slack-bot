import unittest

from bot.models.github import convert_keywords_to_events
from bot.models.slack import Channel
from bot.slack import Runner
from bot.utils.log import Logger
from bot.utils.storage import Storage

from ..utils.comparators import Comparators
from ..utils.load import load_test_data


class RunnerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Fetch test data
        cls.data = load_test_data('slack')

        # Construct common Runner instance.
        logger = Logger(0)
        cls.runner = Runner(logger)

    def setUp(self):
        self.runner.subscriptions = Storage.import_subscriptions()

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
