# tests/test_clean_name.py
from get10K import Extractor

def test_clean_name_removes_suffixes():
    name = "Microsoft Corporation"
    cleaned = Extractor.clean_name(name)
    assert cleaned == "microsoft"
