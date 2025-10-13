# tests/test_item_extractor.py
from Itemextractor import extract_item7_item8

def test_item7_and_item8_extraction_from_sample():
    """
    Test that the Item 7 and Item 8 sections are correctly extracted
    from a sample 10-K HTML file.
    """

    # 1️⃣ Load a local HTML file (download one 10-K manually and place it here)
    with open("tests/sample_data/msft_10k_2023.html", encoding="utf-8") as f:
        html = f.read()

    # 2️⃣ Run the extractor
    result = extract_item7_item8(html)

    # 3️⃣ Basic sanity checks
    assert result.item_7 is not None, "Item 7 text should not be None"
    assert result.item_8 is not None, "Item 8 text should not be None"

    # 4️⃣ Check that we captured enough content (not just a heading)
    assert len(result.item_7) > 2000, "Item 7 content seems too short"
    assert len(result.item_8) > 2000, "Item 8 content seems too short"

    # 5️⃣ Keyword sanity checks (flexible, to allow for variations)
    assert "management" in result.item_7.lower() or "discussion" in result.item_7.lower(), \
        "Item 7 should contain MD&A keywords"
    assert "financial" in result.item_8.lower() or "statements" in result.item_8.lower(), \
        "Item 8 should contain financial keywords"
