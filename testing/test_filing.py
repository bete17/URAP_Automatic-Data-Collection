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
        mock_df = pd.DataFrame({
            'cik': ['0000001750'],
            'fiscal_year': [2023],
            'accession_number': ['0001047469-19-004266'],
            'primary_doc': ['a2239223z10-k.htm'],
            'report_date': ['2019-05-31']
        })
        with patch('filing.pd.read_csv', return_value=mock_df):
            extractor = Extract_Filing(
                user_agent="john@email.com",
                cik="0000001750",
                fiscal_year=2023,
                company="Test Company",
                submission_filepath="data/submission.csv"
            )
            submission = extractor.get_submission()
            self.assertIsInstance(submission, FilingMeta)
            self.assertEqual(submission.cik, "0000001750")
        
    def test_build_meta(self):
        extractor = Extract_Filing(
            user_agent="john@email.com",
            cik="0000001750",
            fiscal_year=2023,
            company="Test Company",
            submission_filepath="data/submission.csv"
        )
        company = "AIR"
        cik = "0000001750"
        fiscal_year = 2019
        form = "10-K"
        accession = "0001047469-19-004266"
        primary_doc = "a2239223z10-k.htm"
        report_date = "2019-05-31"
        meta = extractor.build_meta(company, cik, fiscal_year, form, accession, primary_doc, report_date) 
        self.assertIsInstance(meta, FilingMeta)
        self.assertEqual(meta.company, company)
        self.assertEqual(meta.cik, cik)
        self.assertEqual(meta.fiscal_year, fiscal_year)
        self.assertEqual(meta.form, form)
        self.assertEqual(meta.accession, accession)
        self.assertEqual(meta.primary_doc, primary_doc)
        self.assertEqual(meta.report_date, report_date)
        
    def test_fetch_10k(self):
        extractor = Extract_Filing(
            user_agent="john@email.com",
            cik="0000001750",
            fiscal_year=2023,
            company="Test Company",
            submission_filepath="data/submission.csv"
        )
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
        with patch.object(extractor, 'request_web') as mock_req:
            mock_req.return_value.text = "<html><body>10-K content</body></html>"
            html = extractor.fetch_10k(meta)
            self.assertIsInstance(html, str)
            self.assertGreater(len(html), 10)
            self.assertIn("<html", html.lower())
            self.assertIn("</html>", html.lower())

if __name__ == "__main__":
    unittest.main()