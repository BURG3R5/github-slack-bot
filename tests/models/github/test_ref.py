import unittest

from bot.models.github.ref import Ref


class RefTest(unittest.TestCase):

    def test_should_create_Ref(self):
        ref = Ref(name="hey, this is unittest ref", ref_type="branch")
        self.assertEqual(str(ref), "hey, this is unittest ref")
