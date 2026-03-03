from dataclasses import dataclass
from typing import List, Literal, Optional

BlockType = Literal["paragraph", "table"]

@dataclass
class Block:
    """
    Represents a block of elements extracted from a 10k.
    Can be a paragraph or a table.
    """
    type: BlockType                   # "paragraph" or "table"
    text: Optional[str] = None        # for paragraphs
    rows: Optional[List[List[str]]] = None  # for tables
    
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
    url: str


@dataclass
class ItemSections:
    """
    Holds the extracted Item 7 and Item 8 from a 10-K filing.
    """
    item7_blocks: List[Block]
    item8_blocks: List[Block]
    source_url: Optional[str] = None