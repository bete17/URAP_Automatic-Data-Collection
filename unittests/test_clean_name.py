# tests/test_clean_name.py
import unittest
from Code.src.extractFile import Extractor

class TestExtractor(unittest.TestCase):

    def test_clean_name(self):
        name = "Microsoft Corporation"
        cleaned = Extractor.clean_name(name)
        self.assertEqual(cleaned, "microsoft")
