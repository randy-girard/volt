import unittest

from volt.utils.regex_engine import RegexEngine
from volt.models.profile import Profile

class RegexEngineTest(unittest.TestCase):
    def test_another_ch_example(self):
        engine = RegexEngine(None)
        engine.compile("\*\*A Magic Die is rolled by {s}.")
        matches = engine.match("**A Magic Die is rolled by Moonglade.")
        print(matches)
        result = engine.execute("{s}", matches=matches)
        self.assertEqual(result, "Moonglade")
