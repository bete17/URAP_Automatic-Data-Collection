import os
import csv
import re
from tempfile import template
from typing import Optional, Dict, List, Tuple, Set
from bs4 import BeautifulSoup, Tag
from dataclass import ItemSections, Block


class Extract_Restructure:
    
    @staticmethod
    def _norm(s: str) -> str:
        """Normalize text by replacing non-breaking spaces and cleaning whitespace.

        Args:
            s (str) : The input string to normalize

        Returns:
            str: The normalized string.
        """
        s = (s or "").replace("\xa0", " ")
        s = re.sub(r"[\s–—\-:._]+", " ", s, flags=re.UNICODE)
        return s.strip()

    @staticmethod
    def stream_until_stop(start_tag):
        """Extract content from 'start_tag' until the next section item

        Args:
            start_tag (Tag): The starting tag (<b>, <strong>) from which to extract content

        Returns:
            List[Block]: list of paragraphs and tables
        """
        blocks: List[Block] = []
        current_paragraphs: List[str] = []
        
        for el in start_tag.next_elements:
             # Only work with tags (skip NavigableString etc.)
            if not isinstance(el, Tag):
                continue

            # Stop when we hit the next section heading
            t = el.get_text(" ", strip=True)
            if re.match(r"^\s*item\s*(7a|8|9)\b", t, re.I):
                break

            # Skip obvious non-content
            if el.name in ("script", "style"):
                continue

            # 1) Handle tables ONCE, and skip collecting their inner <p> separately
            if el.name == "table":
                rows = []
                for row in el.find_all("tr"):
                    cells = [
                        Extract_Restructure._norm(cell.get_text(" ", strip=True))
                        for cell in row.find_all(["td", "th"])
                    ]
                    if cells:
                        rows.append(cells)
                if rows:
                    blocks.append(Block(type="table", rows=rows))
                # continue so we don't also treat descendants as standalone blocks
                continue

            # 2) Handle paragraphs, but NOT those inside a table (avoid duplication)
            if el.name == "p" and not el.find_parent("table"):
                txt = el.get_text(" ", strip=True)
                if txt:
                    blocks.append(Block(type="paragraph", text=txt))
                continue
                
        return blocks
    
    
    def find_item7_tag(self, soup):
        """Find the tag that represent the item 7 headings which is usually under <b> or <strong>

        Args:
            soup (BeautifulSoup): The parsed HTML document

        Returns:
            Tag: The tag representing the item 7 heading
        """
        candidates = []
        #find all the relevant tags
        for b in soup.find_all(["b", "strong"]):
            txt = b.get_text(" ", strip=True)
            if re.match(r"^\s*item\s*7\b", txt, re.I):
                candidates.append(b)

        best_tag = None
        best_len = 0

        for tag in candidates:
            # skip TOC (Table Of Contents) entries
            if tag.find_parent(["ul", "ol", "table"]):
                continue

            # slice forward until 7A/8/9
            collected= Extract_Restructure.stream_until_stop(tag)
            if len(collected) > best_len:
                best_tag, best_len = tag, len(collected)
        return best_tag
    
    
    def find_item8_tag(self, soup):
        """Find the tag that represent the item 8 headings which is usually under <b> or <strong>

        Args:
            soup (BeautifulSoup): The parsed HTML document

        Returns:
            Tag: The tag representing the item 8 heading
        """
        candidates = []
        for b in soup.find_all(["b", "strong"]):
            txt = b.get_text(" ", strip=True)
            if re.match(r"^\s*item\s*8\b", txt, re.I):
                candidates.append(b)

        best_tag = None
        best_len = 0

        for tag in candidates:
            # skip TOC entries
            if tag.find_parent(["ul", "ol", "table"]):
                continue

            # slice forward until item 9
            collected = Extract_Restructure.stream_until_stop(tag)
            # find the tag with the most content
            if len(collected) > best_len:
                best_tag, best_len = tag, len(collected)
            
            # if item 8 is on a different page
            
            
        return best_tag
    
    
    
    
    def extract_items(self, html):
        """Extract item 7 and item 8 sections from the HTML document.

        Args:
            html (str): The HTML content to parse.

        Returns:
            ItemSections: An object containing the extracted blocks for each item.
        """
        soup = BeautifulSoup(html, 'html.parser')

        item7_blocks = self.stream_until_stop(self.find_item7_tag(soup))
        item8_blocks= self.stream_until_stop(self.find_item8_tag(soup))

        return ItemSections(
            item7_blocks=item7_blocks,
            item8_blocks=item8_blocks,
            source_url=None,
        )
        
    def stream_blocks(self, blocks: List[Block]):
        """Normalize all the paragraphs and table

        Args:
            blocks (List[Block]): lists of blocks to normalize

        Returns:
            LList[Block]: The normalized list of blocks
        """
        for block in blocks:
            if block.type == "paragraph":
                block.text = self._norm(block.text)
            elif block.type == "table":
                normalized_rows = []
                for row in block.rows:
                    normalized_row = [self._norm(cell) for cell in row]
                    normalized_rows.append(normalized_row)
                block.rows = normalized_rows
        return blocks
    
    def is_restructuring(self, blocks):
        """Check whether a paragraph/table is restructuring-related through keywords search

        Args:
            blocks (List[Block]): paragraphs/tables to check

        Returns:
            bool: True or False
        """
        keywords = ["restructuring",
                "reorganizations?",
                "special\s+charges?",
                "realignment",
                "repositioning",
                "asset\s+impairment",
                "layoff\s+costs?",
                "employee\s+termination",
                "workforce\s+reduction"
            ]
        
        if not keywords:
            return False

        # build regex that matches any keyword as a whole phrase
        pattern = re.compile(r"\b(?:%s)\b" % "|".join(keywords), re.I)

        for block in blocks or []:
            if block is None:
                continue

            text = None
            # Paragraph blocks have `text`; tables have `rows`
            if getattr(block, "type", None) == "paragraph":
                text = (block.text or "")
            elif getattr(block, "type", None) == "table":
                rows = block.rows or []
                # Flatten table cells into searchable text
                row_texts = ["\t".join(cell for cell in row if cell) for row in rows]
                text = "\n".join(row_texts)
            elif isinstance(block, str):
                text = block
            else:
                # Unknown block shape — skip
                continue

            if text and pattern.search(text):
                return True

        return False
    
    def capture_hits(self, wanted_blocks):
        """Collect all the restructuring-related paragraphs/tables

        Args:
            wanted_blocks (List[Block]): Item 7 or Item 8 blocks

        Returns:
            List[Dict]: A list of dictionaries containing the index and block for each hit
        """
        
        # Normalize blocks first (safe to call with empty list)
        blocks = self.stream_blocks(wanted_blocks or [])

        hits = []

        for idx, block in enumerate(blocks):
            try:
                if self.is_restructuring([block]):
                    hits.append({
                        "index": idx,
                        "block": block,
                    })
            except Exception:
                # Skip problematic blocks but continue processing
                continue

        return hits
    
    def merge_adjacent(self, blocks):
        #Merge adjacent blocks into one larger block.
        None
    

    def get_restructure(self, sections_or_html) -> List[str]:
        """Full pipeline from the html to the restructuring-related item 7 and 8 paragraphs/tables cleaned and in text format
        
        Args:
            sections_or_html (str/ItemSections):Either the raw html or the extracted items

        Returns:
            List[str]: A list of restructuring-related paragraphs/tables in text format
        """
        # Accept either HTML or ItemSections
        if isinstance(sections_or_html, str):
            sections = self.extract_items(sections_or_html)
        else:
            sections = sections_or_html

        results: List[str] = []

        for blocks in (sections.item7_blocks or [], sections.item8_blocks or []):
            # normalize blocks first
            normalized = self.stream_blocks(blocks)
            hits = self.capture_hits(normalized)
            for rec in hits:
                block = rec.get("block")
                if getattr(block, "type", None) == "paragraph":
                    text = (block.text or "").strip()
                elif getattr(block, "type", None) == "table":
                    rows = block.rows or []
                    text = "\n".join("\t".join(cell for cell in row if cell) for row in rows)
                elif isinstance(block, str):
                    text = block
                else:
                    text = repr(block)

                if text:
                    results.append(text)

        return results
        
    