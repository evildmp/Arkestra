import unittest

from arkestra_utilities.text import concatenate


class TestConcatenate(unittest.TestCase):
    def test_concatenate_with_no_arguments(self):
        self.assertEqual(concatenate(), "")

    def test_concatenate_with_no_strings(self):
        self.assertEqual(
            concatenate(with_string="-"),
            ""
            )

    def test_concatenate_with_strings(self):
        self.assertEqual(
            concatenate(strings=["La", "vita", "nuda"]),
            "Lavitanuda"
            )

    def test_concatenate_with_strings_and_with_strings(self):
        self.assertEqual(
            concatenate(with_string="-", strings=["La", "vita", "nuda"]),
            "La-vita-nuda"
            )

    def test_concatenate_with_unnamed_arguments(self):
        self.assertEqual(
            concatenate(["La", "vita", "nuda"], "-"),
            "La-vita-nuda"
            )
