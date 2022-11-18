import unittest

from bottle import MultiDict

from bot.utils.json import JSON


class JSONTest(unittest.TestCase):

    def test_getitem_empty(self):
        json = JSON({})
        self.assertEqual("NAME", json["name"])

    def test_getitem_not_found(self):
        json = JSON({"login": "exampleuser"})
        self.assertEqual("NAME", json["name"])

    def test_getitem_found(self):
        json = JSON({"name": "exampleuser"})
        self.assertEqual("exampleuser", json["name"])

    def test_getitem_found_first(self):
        json = JSON({"name": "exampleuser"})
        self.assertEqual("exampleuser", json["name", "login"])

    def test_getitem_found_second(self):
        json = JSON({"login": "exampleuser"})
        self.assertEqual("exampleuser", json["name", "login"])

    def test_getitem_multiple_not_found(self):
        json = JSON({})
        self.assertEqual("NAME", json["name", "login"])

    def test_from_multi_dict(self):
        multi_dict = MultiDict({
            "name": "exampleuser",
            "login": "example_user"
        })

        json = JSON.from_multi_dict(multi_dict)

        self.assertEqual({
            "name": "exampleuser",
            "login": "example_user"
        }, json.data)
