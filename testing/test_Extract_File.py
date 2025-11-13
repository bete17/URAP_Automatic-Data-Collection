# tests/test_get_cik.py
import os
import sys
import unittest
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(ROOT, "src"))

from filing import Extractor
from dataclass import FilingMeta

class TestExtractor(unittest.TestCase):
    """Test whether extractor sucesfully obtain the html file and that it got the right file"""

    def test_fetch_10k(self):
        # Arrange
        extractor = Extractor()
        meta = FilingMeta(
            company="AIR",
            cik="0000001750",
            fiscal_year=2019,
            form="10-K",
            accession="0001047469-19-004266",
            primary_doc="a2239223z10-k.htm",
            report_date="2019-05-31",
            url="https://www.sec.gov/Archives/edgar/data/1750/000104746919004266/a2239223z10-k.htm"
        )

        # Act
        html = extractor.fetch_10k(meta)

       # Assert
        self.assertIsInstance(html, str)
        self.assertGreater(len(html), 1000)  # file is large → sanity check
        self.assertIn("<html", html.lower())
        self.assertIn("</html>", html.lower())
        
if __name__ == "__main__":
    unittest.main()