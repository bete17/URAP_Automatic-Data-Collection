from dataclasses import dataclass
from typing import Optional


@dataclass
class FilingMeta:
    """
    Holds metadata about a single SEC filing (e.g., 10-K).
    This makes it easier to pass filing info between steps.
    """
    company: str
    cik: str
    fiscal_year: int
    form: str
    accession: str
    primary_doc: str
    report_date: Optional[str]
    filing_date: Optional[str]
    url: str
    is_amendment: bool = False


@dataclass
class ItemSections:
    """
    Holds the extracted text for Item 7 and Item 8 of a 10-K.
    """
    item_7: Optional[str]
    item_8: Optional[str]
    source_url: Optional[str] = None