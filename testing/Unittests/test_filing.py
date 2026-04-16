# tests/test_filing.py
import os
import sys
import unittest
import tempfile
import pandas as pd
from unittest.mock import patch, MagicMock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from filing import Extract_Filing, ARCHIVES_BASE
from dataclass import FilingMeta
from savefile import FileExporter


class Testfiling(unittest.TestCase):
    _csv_path = os.path.join("data", "submission.csv")

    def test_get_submission(self):
        mock_df = pd.DataFrame({
            "cik": ["0000001750"],
            "fiscal_year": [2023],
            "accession_number": ["0001047469-19-004266"],
            "primary_doc": ["a2239223z10-k.htm"],
            "report_date": ["2019-05-31"],
        })
        with patch("filing.pd.read_csv", return_value=mock_df) as mock_read:
            extractor = Extract_Filing(
                user_agent="john@email.com",
                cik="0000001750",
                fiscal_year=2023,
                company="Test Company",
            )
            submission = extractor.get_submission(self._csv_path)
            mock_read.assert_called_once_with(
                self._csv_path, dtype={"cik": str}
            )
        self.assertIsInstance(submission, FilingMeta)
        self.assertEqual(submission.cik, "0000001750")
        self.assertEqual(submission.fiscal_year, 2023)
        self.assertEqual(submission.company, "Test Company")
        self.assertEqual(submission.form, "10-K")
        self.assertEqual(submission.accession, "0001047469-19-004266")
        self.assertEqual(submission.primary_doc, "a2239223z10-k.htm")
        self.assertEqual(submission.report_date, "2019-05-31")
        expected_url = (
            f"{ARCHIVES_BASE}/edgar/data/1750/"
            "000104746919004266/a2239223z10-k.htm"
        )
        self.assertEqual(submission.url, expected_url)

    def test_get_submission_empty_returns_none(self):
        mock_df = pd.DataFrame({
            "cik": ["9999999999"],
            "fiscal_year": [2023],
            "accession_number": ["x"],
            "primary_doc": ["y"],
        })
        with patch("filing.pd.read_csv", return_value=mock_df):
            extractor = Extract_Filing(
                user_agent="john@email.com",
                cik="0000001750",
                fiscal_year=2023,
                company="Test Company",
            )
            self.assertIsNone(extractor.get_submission(self._csv_path))

    def test_get_submission_no_report_date_column(self):
        mock_df = pd.DataFrame({
            "cik": ["0000001750"],
            "fiscal_year": [2023],
            "accession_number": ["0001047469-19-004266"],
            "primary_doc": ["a2239223z10-k.htm"],
        })
        with patch("filing.pd.read_csv", return_value=mock_df):
            extractor = Extract_Filing(
                user_agent="john@email.com",
                cik="0000001750",
                fiscal_year=2023,
                company="Test Company",
            )
            submission = extractor.get_submission(self._csv_path)
        self.assertIsNone(submission.report_date)

    def test_build_meta(self):
        company = "AIR"
        cik = "0000001750"
        fiscal_year = 2019
        form = "10-K"
        accession = "0001047469-19-004266"
        primary_doc = "a2239223z10-k.htm"
        report_date = "2019-05-31"
        meta = Extract_Filing.build_meta(
            company, cik, fiscal_year, form, accession, primary_doc, report_date
        )
        self.assertIsInstance(meta, FilingMeta)
        self.assertEqual(meta.company, company)
        self.assertEqual(meta.cik, cik)
        self.assertEqual(meta.fiscal_year, fiscal_year)
        self.assertEqual(meta.form, form)
        self.assertEqual(meta.accession, accession)
        self.assertEqual(meta.primary_doc, primary_doc)
        self.assertEqual(meta.report_date, report_date)
        expected_url = (
            f"{ARCHIVES_BASE}/edgar/data/1750/"
            "000104746919004266/a2239223z10-k.htm"
        )
        self.assertEqual(meta.url, expected_url)

    def test_build_meta_empty_report_date(self):
        meta = Extract_Filing.build_meta(
            "AIR",
            "0000001750",
            2019,
            "10-K",
            "0001047469-19-004266",
            "a2239223z10-k.htm",
            "",
        )
        self.assertIsNone(meta.report_date)

    def test_fetch_10k(self):
        extractor = Extract_Filing(
            user_agent="john@email.com",
            cik="0000001750",
            fiscal_year=2023,
            company="Test Company",
        )
        meta = FilingMeta(
            company="AIR",
            cik="0000001750",
            fiscal_year=2019,
            form="10-K",
            accession="0001047469-19-004266",
            primary_doc="a2239223z10-k.htm",
            report_date="2019-05-31",
            url=(
                "https://www.sec.gov/Archives/edgar/data/1750/"
                "000104746919004266/a2239223z10-k.htm"
            ),
        )
        mock_resp = MagicMock()
        mock_resp.text = "<html><body>10-K content</body></html>"
        with patch.object(extractor, "request_web", return_value=mock_resp):
            html = extractor.fetch_10k(meta)
        self.assertIsInstance(html, str)
        self.assertGreater(len(html), 10)
        self.assertIn("<html", html.lower())
        self.assertIn("</html>", html.lower())

    def test_fetch_10k_returns_none_when_request_fails(self):
        extractor = Extract_Filing(
            user_agent="john@email.com",
            cik="0000001750",
            fiscal_year=2023,
            company="Test Company",
        )
        meta = FilingMeta(
            company="AIR",
            cik="0000001750",
            fiscal_year=2019,
            form="10-K",
            accession="0001047469-19-004266",
            primary_doc="a2239223z10-k.htm",
            report_date="2019-05-31",
            url="https://www.sec.gov/Archives/edgar/data/1750/000104746919004266/x.htm",
        )
        with patch.object(extractor, "request_web", return_value=None):
            self.assertIsNone(extractor.fetch_10k(meta))

    def test_get_html(self):
        extractor = Extract_Filing(
            user_agent="john@email.com",
            cik="0000001750",
            fiscal_year=2023,
            company="Test Company",
        )
        meta = FilingMeta(
            company="AIR",
            cik="0000001750",
            fiscal_year=2023,
            form="10-K",
            accession="0001047469-19-004266",
            primary_doc="a2239223z10-k.htm",
            report_date="2019-05-31",
            url="https://www.sec.gov/Archives/edgar/data/1750/000104746919004266/a2239223z10-k.htm",
        )
        with patch.object(extractor, "get_submission", return_value=meta):
            with patch.object(
                extractor, "fetch_10k", return_value="<html>ok</html>"
            ):
                html = extractor.get_html(self._csv_path)
        self.assertEqual(html, "<html>ok</html>")

        with patch.object(extractor, "get_submission", return_value=None):
            self.assertIsNone(extractor.get_html(self._csv_path))

    def test_save_restructuring_filename_format(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            item7_dir = os.path.join(tmpdir, "item7")
            item8_dir = os.path.join(tmpdir, "item8")
            exporter = FileExporter(
                output_dir_7=item7_dir,
                output_dir_8=item8_dir,
                cik="0000001750",
                year=2023,
            )

            with patch.object(exporter, "get_gvkey", return_value="012345"):
                exporter.save_restructuring(item7_hits=[], item8_hits=[])

            self.assertTrue(os.path.exists(os.path.join(item7_dir, "012345_2023_item7.txt")))
            self.assertTrue(os.path.exists(os.path.join(item8_dir, "012345_2023_item8.txt")))


if __name__ == "__main__":
    unittest.main()
