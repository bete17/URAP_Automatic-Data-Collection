# tests/test_get_cik.py
import os
import sys
import unittest
from unittest.mock import patch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(ROOT, "src"))

from extractFile import Extractor  # <- match your actual module name

class TestExtractor(unittest.TestCase):
    def test_get_cik(self):
        fake_json = {
            "0": {"title": "Microsoft Corporation", "cik_str": 789019}
        }

        class Resp:
            def raise_for_status(self): pass
            def json(self): return fake_json

        with patch("extractFile.requests.get", return_value=Resp()):
            ext = Extractor()
            cik = ext.get_cik("Microsoft Corporation")
            self.assertEqual(cik, "0000789019")

if __name__ == "__main__":
    unittest.main()
