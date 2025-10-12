# item_extractor.py (or add into extractor.py)
import re
from typing import Optional, List, Tuple
from bs4 import BeautifulSoup
from models import ItemSections

# Compile once
ITEM7_RE   = re.compile(r'^\s*item\s*7\s*[\.\:\- ]*(management|md&a|$)', re.I)
ITEM7A_RE  = re.compile(r'^\s*item\s*7a\b', re.I)
ITEM8_RE   = re.compile(r'^\s*item\s*8\s*[\.\:\- ]*(financial|$)', re.I)
ITEM9_RE   = re.compile(r'^\s*item\s*9\b', re.I)

MDNA_HINT  = re.compile(r'\b(md&a|management|discussion|analysis)\b', re.I)
TOC_DOTS   = re.compile(r'\.{3,}')  # dot leaders "....."
WHITESPACE = re.compile(r'\s+')

BLOCK_TAGS = ['h1','h2','h3','h4','h5','h6','p','div','b','strong','font']

def _norm(t: str) -> str:
    return WHITESPACE.sub(' ', t or '').strip()

def _is_toc_line(txt: str) -> bool:
    return bool(TOC_DOTS.search(txt)) or 'table of contents' in txt.lower()

def _anchor_near(tag) -> bool:
    prev = tag.find_previous(lambda t: t.name == 'a' and (t.get('name') or t.get('id')), limit=1)
    nxt  = tag.find_next(lambda t: t.name == 'a' and (t.get('name') or t.get('id')), limit=1)
    for a in filter(None, [prev, nxt]):
        v = (a.get('name') or a.get('id') or '').lower()
        if 'item7' in v or v.strip() in {'7', 'item_7'}:
            return True
    return False

def _next_item_idx(blocks: List[Tuple[object, str]], start_i: int) -> Optional[int]:
    """Find index of the next major item heading after start_i."""
    for j in range(start_i + 1, len(blocks)):
        t = blocks[j][1]
        if ITEM7A_RE.search(t) or ITEM8_RE.search(t) or ITEM9_RE.search(t):
            return j
    return None

def extract_item7_item8(html: str, require_min_chars: int = 2000) -> ItemSections:
    soup = BeautifulSoup(html, 'html.parser')

    # Build linear blocks (tag, text)
    blocks: List[Tuple[object, str]] = []
    for tag in soup.find_all(BLOCK_TAGS):
        txt = _norm(tag.get_text(" ", strip=True))
        if txt:
            blocks.append((tag, txt))

    # Score Item 7 candidates
    candidates: List[Tuple[int, int]] = []  # (index, score)
    for i, (tag, txt) in enumerate(blocks):
        if ITEM7_RE.search(txt):
            score = 2  # base score for heading match (start-anchored)
            if _anchor_near(tag): score += 1
            if _is_toc_line(txt): score -= 1

            nxt = _next_item_idx(blocks, i)
            if nxt is not None:
                nxt_txt = blocks[nxt][1]
                # sane sequence bonus (7 -> 7A or 8)
                if ITEM7A_RE.search(nxt_txt) or ITEM8_RE.search(nxt_txt):
                    score += 1
                # MD&A hint bonus in the local body
                body_preview = ' '.join(b[1] for b in blocks[i:nxt])[:400]
                if MDNA_HINT.search(body_preview):
                    score += 1
                # length check: if too short until next heading, downrank
                body_chars = sum(len(b[1]) + 1 for b in blocks[i:nxt])
                if body_chars < require_min_chars:
                    score -= 1
            candidates.append((i, score))

    if not candidates:
        # Fallback: return empties; your caller can decide next steps
        return ItemSections(item_7=None, item_8=None)

    # Pick best Item 7 (score desc, then earliest)
    candidates.sort(key=lambda x: (-x[1], x[0]))
    i7 = candidates[0][0]
    j7 = _next_item_idx(blocks, i7) or len(blocks)

    # Now find Item 8 start AFTER chosen Item 7
    i8 = None
    for k in range(i7 + 1, len(blocks)):
        if ITEM8_RE.search(blocks[k][1]):
            i8 = k
            break
    j8 = _next_item_idx(blocks, i8) if i8 is not None else None

    item7_text = ' '.join(b[1] for b in blocks[i7:j7]) if i7 is not None else None
    item8_text = ' '.join(b[1] for b in blocks[i8:j8]) if i8 is not None else None

    return ItemSections(item_7=item7_text, item_8=item8_text)
