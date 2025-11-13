# tests/test_item_extractor.py
import os
import sys
import unittest
from unittest.mock import patch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(ROOT, "src"))

from Extract_Items import Extract_Restructure

def test_item7_and_item8_extraction_from_sample():
    """
    Test that the Item 7 and Item 8 sections are correctly extracted
    from a sample 10-K HTML file.
    """

