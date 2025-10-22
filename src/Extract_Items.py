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