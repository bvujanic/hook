from .context import Upserter
import json
import unittest


def invalid_schema():
    payload = json.loads('{"device": 42, "rps": 37, "errors": 3.7462143364999947, "time_taken": 2.3813013475306977}')
    return Upserter.validate_schema(payload)


def valid_schema():
    payload = json.loads('{"device": "galaxy", "rps": 37, "errors": 3.7462143364999947, "time_taken": 2.3813013475306977}')
    return Upserter.validate_schema(payload)


class UpserterTests(unittest.TestCase):
    def test_invalid_schema(self):
        with self.assertRaises(Exception) as context:
            invalid_schema()
        self.assertTrue("Invalid json schema" in str(context.exception))

    def test_valid_schema(self):

        is_valid = valid_schema()
        self.assertTrue(is_valid)
