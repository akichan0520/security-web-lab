import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import lookup, SEED

class TestLocalCTF(unittest.TestCase):
    def test_normal_value(self):
        for vulnerable in (False, True):
            self.assertEqual(lookup('Travel Kit', vulnerable), [('Travel Kit',2500)])

    def test_boolean_true_in_vulnerable_only(self):
        attack = "' OR '1'='1' -- "
        self.assertEqual(len(lookup(attack, True)), len(SEED))
        self.assertEqual(lookup(attack, False), [])

    def test_boolean_false(self):
        attack = "' OR '1'='2' -- "
        self.assertEqual(lookup(attack, True), [])
        self.assertEqual(lookup(attack, False), [])

    def test_quote_errors_only_in_vulnerable(self):
        import sqlite3
        with self.assertRaises(sqlite3.Error): lookup("'", True)
        self.assertEqual(lookup("'", False), [])

if __name__ == '__main__': unittest.main()
