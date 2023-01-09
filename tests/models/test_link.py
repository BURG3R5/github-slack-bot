import unittest

from bot.models.link import Link


class LinkTest(unittest.TestCase):

    def test_should_make_link(self):
        link = Link(url="www.unittest.com", text="unittest")
        self.assertEqual(str(link), "<www.unittest.com|unittest>")

    def test_should_make_link_without_url(self):
        link = Link(text="unittest1")
        self.assertEqual(str(link), "<None|unittest1>")

    def test_should_make_link_without_text(self):
        link = Link(text="www.unittest1.com")
        self.assertEqual(str(link), "<None|www.unittest1.com>")
