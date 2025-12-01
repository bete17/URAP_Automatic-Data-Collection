# item_extractor.py
import re
from tempfile import template
from typing import Optional, Dict, List, Tuple, Set
from bs4 import BeautifulSoup, Tag
from dataclass import ItemSections, Block


class Extract_Restructure:
    #Constructor
    keywords = ["restructuring",
                "rationalization",
                "reorganization",
                "realignment",
                "repositioning",
                "divestiture of asset and business",
                "asset impairment",
                "layoff cost",
                "employee termination",
                "workforce reduction"
    ]
    
    def __init__(self):
        pass
    
    #------------------- Helper Functions -----------------------###
    @staticmethod
    def _norm(s: str) -> str:
        s = (s or "").replace("\xa0", " ")
        s = re.sub(r"[\s–—\-:._]+", " ", s, flags=re.UNICODE)
        return s.strip()
    
    @staticmethod
    def stream_until_stop(start_tag):
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
                        row.append(cells)
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
                
        #Join all collected text chunks into a single string
        joined = "\n".join(text_chunks)
        return joined
    
    
    def find_item7_tag(soup):
        candidates = []
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

            # slice forward until 7A/8/9
            collected = Extract_Restructure.stream_until_stop(tag)
            if len(collected) > best_len:
                best_tag, best_len = tag, len(collected)
        return best_tag
    ###-----------------------Helper functions end--------------------###
    
    
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
        #Transform/Normalize item sections for simplicity (easier to analyze)
        
        None
    
    def score_block(self, block):
        #Give a score to a block based on relevancy to restructuring
        None
    
    def is_restructuring(self,block):
        #Determine if a block is about restructuring
        None
        
    def capture_hits(self, wanted_blocks):
        #Aggregate all relevant blocks within one section.
        None
    
    def merge_adjacent(self, blocks):
        #Merge adjacent blocks into one larger block.
        None
    
    def write_out(self, hits, filepath):
        #Write the extracted sections to an output file.
        None
        
    