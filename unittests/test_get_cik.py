# tests/test_get_cik.py
import requests
from get10K import Extractor

def test_get_cik(monkeypatch):
    fake_json = {
        "0": {"title": "Microsoft Corporation", "cik_str": 789019}
    }

    def fake_get(*args, **kwargs):
        class Resp:
            def raise_for_status(self): pass
            def json(self): return fake_json
        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)
    ext = Extractor()
    cik = ext.get_cik("Microsoft Corporation")
    assert cik == "0000789019"
