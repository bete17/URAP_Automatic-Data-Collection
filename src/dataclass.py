from dataclass import dataclass

@dataclass
class FillingMeta:
    company: str
    cik: str
    fiscal_year: int
    form: str
    accession: str
    primary_doc: str
    report_date: Optional[str] = None
    filing_date: Optional[str] = None
    url: Optional[str] = None
    is_amendment: bool = False
    
@dataclass
class ItemSections:
    item7: str
    item8: str
    raw_html_url: Optional[str] = None