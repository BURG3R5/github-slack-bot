import unittest

from bot.models.github.event_type import EventType
from bot.models.slack import Channel


class ChannelTest(unittest.TestCase):

    def test_should_make_channel_str(self):
        channel = Channel("unittest_channel", [
            EventType.BRANCH_CREATED, EventType.COMMIT_COMMENT, EventType.FORK
        ])
        self.assertEqual(str(channel), "unittest_channel")

    def test_is_subscribed_to(self):
        channel = Channel("unittest_channel", [
            EventType.BRANCH_CREATED, EventType.COMMIT_COMMENT, EventType.FORK
        ])
        self.assertEqual([
            EventType.BRANCH_CREATED, EventType.COMMIT_COMMENT, EventType.FORK
        ], is_subs)
