from bot.slack.runner import Runner

from .base import MockSlackBotBase

TestableRunner = type(
    'TestableRunner',
    (MockSlackBotBase, ),
    dict(Runner.__dict__),
)
