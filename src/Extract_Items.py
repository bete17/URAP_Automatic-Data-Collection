# item_extractor.py
import re
from typing import Optional, Dict, List, Tuple, Set
from bs4 import BeautifulSoup, NavigableString, Tag
from dataclass import ItemSections

ITEM7_RE   = re.compile(r"^\s*item\s*7\b", re.I)
ITEM7A_RE  = re.compile(r"^\s*item\s*7\s*a\b", re.I)
ITEM8_RE   = re.compile(r"^\s*item\s*8\b", re.I)
ITEM9_RE   = re.compile(r"^\s*item\s*9\b", re.I)

BLOCK_TAGS = ("h1","h2","h3","h4","h5","h6","p","div","span","b","strong","font","a")

class Extract_Restructure:
    def __init__(self):
        pass
    
    def extract_items(self, html):
        #Locate Item 7 & 8 on the html page
        None
        
    def stream_blocks(self, meta : ItemSections)
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