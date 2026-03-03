# tests/test_get_cik.py
import os
import sys
import unittest
import pandas as pd
from unittest.mock import patch, MagicMock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(ROOT, "src"))

from filing import Extract_Filing
from dataclass import FilingMeta

class Testfiling(unittest.TestCase):
    
    def test_get_submission(self):
        # Arrange
        extractor = Extract_Filing("0000001750")
        cik = "0000001750"  # Example CIK for testing

        # Act
        submissions = extractor.get_submissions()

        # Assert
        self.assertIsInstance(submissions, dict)
        self.assertIn("filings", submissions)
        
    def test_build_meta(self):
        # Arrange
        extractor = Extract_Filing("0000001750")
        company = "AIR"
        cik = "0000001750"
        fiscal_year = 2019
        form = "10-K"
        accession = "0001047469-19-004266"
        primary_doc = "a2239223z10-k.htm"
        report_date = "2019-05-31"
        # Act
        meta = extractor.build_meta(company, cik, fiscal_year, form, accession, primary_doc, report_date) 
        # Assert
        self.assertIsInstance(meta, FilingMeta)
        self.assertEqual(meta.company, company)
        self.assertEqual(meta.cik, cik)
        self.assertEqual(meta.fiscal_year, fiscal_year)
        self.assertEqual(meta.form, form)
        self.assertEqual(meta.accession, accession)
        self.assertEqual(meta.primary_doc, primary_doc)
        self.assertEqual(meta.report_date, report_date)
        
    def test_choose_10k(self):
        # Arrange
        extractor = Extract_Filing("0000061478")
        company = "ADC TELECOMMUNICATIONS INC"
        submissions = extractor.get_submissions()
        fiscal_year = 2002

        # Act
        meta = extractor.choose_10k(company, submissions, fiscal_year)

        # Assert
        self.assertIsNotNone(meta)
        self.assertIsInstance(meta, FilingMeta)
        self.assertEqual(meta.form, "10-K")
        self.assertEqual(meta.fiscal_year, fiscal_year)
        
    def test_fetch_10k(self):
        # Arrange
        extractor = Extract_Filing("0000001750")
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