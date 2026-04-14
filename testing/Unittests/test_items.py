# tests/test_item_extractor.py
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(ROOT, "src"))

from items import Extract_Restructure
from dataclass import Block
import tempfile
import os
from bs4 import BeautifulSoup

class Testitems(unittest.TestCase):
    def test_stream_until_stop(self):
        """
        Test that this will get all the text from a starting tag
        until hitting a stopping point (Item 7A, 8, or 9).
        """
        html = """
        <html><body>
        <b id="start">Item 7</b>
        <p>First paragraph about business.</p>
        <p>Second paragraph mentioning restructuring and workforce reduction.</p>
        <b>Item 8</b>
        </body></html>
        """

        soup = BeautifulSoup(html, "html.parser")
        start_tag = soup.find("b", {"id": "start"})

        blocks = Extract_Restructure.stream_until_stop(start_tag)
        # Expect at least two paragraph blocks
        self.assertIsInstance(blocks, list)
        self.assertGreaterEqual(len(blocks), 2)
        self.assertEqual(blocks[0].type, "paragraph")
        self.assertIn("First paragraph", blocks[0].text)
    
    def test_find_real_item7(self):
        """
        Test that the correct starting point for Item 7 is identified
        in a sample 10-K HTML file.
        """
        html = """
        <html><body>
        <ul><li><b id="toc">Item 7</b></li></ul>
        <b id="real">Item 7</b>
        <p>Real content about restructuring.</p>
        <b>Item 8</b>
        </body></html>
        """

        soup = BeautifulSoup(html, "html.parser")
        er = Extract_Restructure()
        tag = er.find_item7_tag(soup)
        self.assertIsNotNone(tag)
        # Should pick the real tag, not the TOC one
        self.assertEqual(tag.get("id"), "real")
    
    def test_find_real_item8(self):
        """
        Test that the correct starting point for Item 8 is identified
        in a sample 10-K HTML file.
        """
        html = """
        <html><body>
        <b id="real8">Item 8</b>
        <p>Content for item 8: financial statements</p>
        <b>Item 9</b>
        </body></html>
        """

        soup = BeautifulSoup(html, "html.parser")
        er = Extract_Restructure()
        tag = er.find_item8_tag(soup)
        self.assertIsNotNone(tag)
        self.assertEqual(tag.get("id"), "real8")
    
    def test_is_restructuring(self):
        """
        Test that the restructuring detection works correctly
        on sample blocks of text.
        """
        er = Extract_Restructure()
        # paragraph block matching
        p = Block(type="paragraph", text="We are planning a restructuring and workforce reduction.")
        # table block matching
        t = Block(type="table", rows=[["Metric", "Value"],["Workforce reduction", "100"]])

        self.assertTrue(er.is_restructuring([p]))
        self.assertTrue(er.is_restructuring([t]))
        # non-matching block
        no = Block(type="paragraph", text="This is unrelated text about sales.")
        self.assertFalse(er.is_restructuring([no]))
    
    def test_capture_hits(self):
        """
        Test that both Item 7 and Item 8 are extracted correctly
        from a sample 10-K HTML file.
        """
        er = Extract_Restructure()
        html = """
        <html><body>
        <b>Item 7</b>
        <p>Discussion of operations and restructuring activities.</p>
        <b>Item 8</b>
        <p>Financial data.</p>
        </body></html>
        """
        sections = er.extract_items(html)
        hits7 = er.capture_hits(sections.item7_blocks)
        self.assertGreaterEqual(len(hits7), 1)
        # hit should include index and block
        self.assertIn("index", hits7[0])
        self.assertIn("block", hits7[0])
    
    def test_write_output(self):
        """
        Test that the extracted items are written out correctly
        to the specified output format.
        """
        er = Extract_Restructure()
        # create some dummy hits
        hits = [
            {"index": 0, "block": Block(type="paragraph", text="Restructuring planned.")},
            {"index": 1, "block": Block(type="table", rows=[["a","b"],["restructuring","yes"]])},
        ]

        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        try:
            out = er.write_out(hits, path)
            self.assertTrue(os.path.exists(out))
            with open(out, "r", encoding="utf-8") as fh:
                data = fh.read()
            # Should contain header and at least one hit text
            self.assertIn("index,type,content", data.replace('\r\n','\n').splitlines()[0])
            self.assertIn("Restructuring planned", data)
        finally:
            os.remove(path)
    

