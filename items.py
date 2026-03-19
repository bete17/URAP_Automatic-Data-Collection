import os
import csv
import re
from tempfile import template
from typing import Optional, Dict, List, Tuple, Set
from bs4 import BeautifulSoup, Tag
from dataclass import ItemSections, Block


class Extract_Restructure:
    
    # Normalize text
    @staticmethod
    def _norm(s: str) -> str:
        s = (s or "").replace("\xa0", " ")
        s = re.sub(r"[\s–—\-:._]+", " ", s, flags=re.UNICODE)
        return s.strip()
    
    #Read through the document until next item
    @staticmethod
    def stream_until_stop(start_tag : Tag):
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
        #Take item 7 and 8 from the html document
        soup = BeautifulSoup(html, 'html.parser')

        item7_blocks = self.stream_until_stop(self.find_item7_tag(soup))
        item8_blocks= self.stream_until_stop(self.find_item8_tag(soup))

        return ItemSections(
            item7_blocks=item7_blocks,
            item8_blocks=item8_blocks,
            source_url=None,
        )
        
    def stream_blocks(self, blocks: List[Block]):
        #Transform/Normalize item sections for simplicity
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
        keywords = ["restructuring",
                "reorganization",
                "special charge",
                "realignment",
                "repositioning",
                "asset impairment",
                "layoff cost",
                "employee termination",
                "workforce reduction"
            ]
        kws = [k.lower().strip() for k in keywords if k]
        if not kws:
            return False

        # build regex that matches any keyword as a whole phrase
        kws_pattern = r"|".join(re.escape(k) for k in kws)
        pattern = re.compile(rf"\b(?:{kws_pattern})\b", re.I)

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
        #Aggregate all relevant blocks within one section.
        
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
        if not blocks:
            return None
        merged =  ""
        for block in blocks:
            if block.type != "paragraph":
                raise TypeError("block has to be a paragraph")
            merged += block.text

        return Block(type = "paragraph", text = merged)
    
    def write_out(self, hits, filepath7, filepath8):
        #Write the extracted sections to an output file.
        # Ensure target directory exists
        dirpath = os.path.dirname(filepath7) or "."
        os.makedirs(dirpath, exist_ok=True)

        # Write as CSV with columns: index, type, content
        with open(filepath7, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=["index", "type", "content"] )
            writer.writeheader()

            for hit in hits or []:
                idx = hit.get("index")
                block = hit.get("block")

                if getattr(block, "type", None) == "paragraph":
                    content = (block.text or "").strip()
                    btype = "paragraph"
                elif getattr(block, "type", None) == "table":
                    rows = block.rows or []
                    # join cells with tab, rows with newline
                    content = "\n".join("\t".join(cell for cell in row if cell) for row in rows)
                    btype = "table"
                elif isinstance(block, str):
                    content = block
                    btype = "string"
                else:
                    content = repr(block)
                    btype = getattr(block, "type", "unknown")

                writer.writerow({"index": idx, "type": btype, "content": content})

        return filepath7

    def get_restructure(self, sections_or_html) -> List[str]:
        """Return all text snippets (paragraphs or flattened table text)
        from Item 7 and Item 8 that contain any of the restructuring keywords.

        `sections_or_html` may be either an `ItemSections` object (as returned
        by `extract_items`) or an HTML string.
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
        
    