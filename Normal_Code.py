import os
import re
import time
import requests
from bs4 import BeautifulSoup

#Reused variables
COMPANY_NAME = input("Enter Company Name:")
FISCAL_YEAR = input("Enter Fiscal Year: ")
SEC_BASE = "https://www.sec.gov"
ARCHIVES_BASE = "https://www.sec.gov/Archives"
HEADERS = {
    "User-Agent": "brucetan@berkeley.edu"
}


# Step 1: Obtain CIK

print(f"[1/6] Getting CIK for {COMPANY_NAME!r} ...")
url = "https://www.sec.gov/files/company_tickers.json"
r = requests.get(url, headers=HEADERS, timeout=30)
r.raise_for_status()
tickers_json = r.json()

def _normalize_name(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r'[,.\-&/]+', ' ', s)
    s = re.sub(r'\b(incorporated|inc|corp|corporation|co|ltd|plc|llc|holdings?|group)\b', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

name_map = {}
for rec in tickers_json.values():
    cik = str(rec["cik_str"]).zfill(10)
    title = _normalize_name(rec["title"])
    name_map[title] = cik

norm_name = _normalize_name(COMPANY_NAME)
if norm_name not in name_map:
    raise SystemExit(f"Company not found in SEC list: {COMPANY_NAME!r} (normalized: {norm_name!r})")
CIK = name_map[norm_name]
print(f"    -> CIK = {CIK}")


# Step 2: Fetch submissions JSON for the CIK

print(f"[2/6] Fetching submissions for CIK {CIK} ...")
subs_url = f'https://data.sec.gov/submissions/CIK{CIK}.json'
r = requests.get(subs_url, headers=HEADERS, timeout=30)
r.raise_for_status()
subs = r.json()

recent = subs.get("filings", {}).get("recent", {})
forms         = recent.get("form", [])
accessions    = recent.get("accessionNumber", [])
primary_docs  = recent.get("primaryDocument", [])
report_dates  = recent.get("reportDate", [])
filing_dates  = recent.get("filingDate", [])


# Step 3: Choose the 10-K for the requested fiscal year (by reportDate)

print(f"[3/6] Selecting 10-K for fiscal year {FISCAL_YEAR} (by reportDate) ...")
chosen = None
for form, acc, doc, rdate, fdate in zip(forms, accessions, primary_docs, report_dates, filing_dates):
    if (form or "").upper() == "10-K" and rdate and rdate.startswith(str(FISCAL_YEAR)):
        chosen = {
            "accession": acc,
            "primary_doc": doc,
            "report_date": rdate,
            "filing_date": fdate
        }
        break

if not chosen:
    # Optional fallback: use the most recent 10-K if the reportDate doesn't match
    print("    ! No exact reportDate match")

if not chosen:
    raise SystemExit("No 10-K filings found for this company.")

ACCESSION = chosen["accession"]
PRIMARY_DOC = chosen["primary_doc"]
REPORT_DATE = chosen["report_date"]
FILING_DATE = chosen["filing_date"]


# Step 4: Build filing URLs (primary + index) and fetch HTML

acc_nodash = ACCESSION.replace("-", "")
base_dir = f"{ARCHIVES_BASE}/edgar/data/{int(CIK)}/{acc_nodash}"
primary_url = f"{base_dir}/{PRIMARY_DOC}"
index_url   = f"{base_dir}/{ACCESSION}-index.htm"

def _fetch(url: str) -> requests.Response:
    rr = requests.get(url, headers=HEADERS, timeout=60)
    rr.raise_for_status()
    return rr

print(f"[4/6] Downloading 10-K HTML ...")
html_text = None
try:
    rr = _fetch(primary_url)
    ctype = rr.headers.get("Content-Type", "").lower()
    if "text/html" in ctype or primary_url.lower().endswith((".htm", ".html")):
        html_text = rr.text
except Exception as e:
    print(f"    Primary fetch failed ({e}); will try index fallback.")

if html_text is None:
    # Fallback: fetch index, pick best HTML document
    try:
        idx = _fetch(index_url).text
        soup = BeautifulSoup(idx, "lxml")
        candidates = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            txt = (a.get_text(" ", strip=True) or "").lower()
            if href.lower().endswith((".htm", ".html")) and ("10-k" in txt or "form 10-k" in txt):
                candidates.append(href)
        if not candidates:
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.lower().endswith((".htm", ".html")):
                    candidates.append(href)
        if not candidates:
            raise RuntimeError("Could not identify a 10-K HTML document from the filing index.")
        picked = candidates[0]
        if not picked.startswith("http"):
            picked = requests.compat.urljoin(f"{ARCHIVES_BASE}/", picked.lstrip("/"))
        html_text = _fetch(picked).text
    except Exception as e:
        raise SystemExit(f"Failed to fetch HTML via index fallback: {e}")

print("    -> HTML fetched.")


# Step 5: Convert HTML to text and extract Item 7 (MD&A)

print(f"[5/6] Extracting Item 7 (MD&A) ...")

# HTML -> text
soup = BeautifulSoup(html_text, "lxml")
for tag in soup(["script", "style", "noscript"]):
    tag.decompose()
# add newlines for common block elements
for tag in soup.find_all(["p", "div", "section", "br", "li", "h1", "h2", "h3", "tr"]):
    tag.append("\n")
text = soup.get_text()
text = re.sub(r"\r", "", text)
text = re.sub(r"[ \t\u00A0]+", " ", text)
text = re.sub(r" *\n *", "\n", text)
text = re.sub(r"\n{3,}", "\n\n", text).strip()

# Regex to capture ITEM 7 need item 8 and 7a since right after item 7 it could be 7a or item 8
ITEM7_HEADER_PAT = re.compile(r"(?is)\bitem\s*7\s*(?:\.|:|–|—|-)?\s*management['’`]?s\s+discussion\s+and\s+analysis\b.*?")
ITEM7_BARE_PAT   = re.compile(r"(?is)\bitem\s*7\b")
ITEM7A_PAT       = re.compile(r"(?is)\bitem\s*7\s*A\b")
ITEM8_PAT        = re.compile(r"(?is)\bitem\s*8\b")

# Find start candidates
starts = []
m = ITEM7_HEADER_PAT.search(text)
if m:
    starts.append(m.start())
starts.extend([m.start() for m in ITEM7_BARE_PAT.finditer(text)])

if not starts:
    print("    ! Could not find 'Item 7' markers in text.")
    item7_text = ""
else:
    starts = sorted(set(starts))
    best_span = None
    for s in starts:
        tail = text[s:]
        m7a = ITEM7A_PAT.search(tail)
        m8  = ITEM8_PAT.search(tail)
        rel = [m.start() for m in [m7a, m8] if m]
        if not rel:
            continue
        end_idx = s + min(rel)
        span_len = end_idx - s
        # prefer a reasonably long span
        if span_len > 2000 and (best_span is None or span_len > (best_span[1]-best_span[0])):
            best_span = (s, end_idx)
    if best_span is None:
        # fallback to first boundary even if short
        s = starts[0]
        tail = text[s:]
        rel = [m.start() for m in [ITEM7A_PAT.search(tail), ITEM8_PAT.search(tail)] if m]
        best_span = (s, s + min(rel)) if rel else None

    if best_span is None:
        print("    ! Could not determine Item 7 span.")
        item7_text = ""
    else:
        s, e = best_span
        chunk = text[s:e].strip()
        # trim leading/trailing headers
        chunk = re.sub(r"^\s*(item\s*7[^\n]*\n)+", "", chunk, flags=re.I)
        chunk = re.sub(r"\n\s*(item\s*7a|item\s*8).*$", "", chunk, flags=re.I|re.S)
        item7_text = chunk.strip()

found = bool(item7_text)
print(f"    -> Item 7 found: {found}")

# Step 6: Write to TXT
print(f"[6/6] Writing output TXT ...")
# sanitize for filename: strip whitespace, replace spaces and bad chars
safe_name = COMPANY_NAME.strip()                      # remove leading/trailing spaces/tabs/newlines
safe_name = re.sub(r"[^\w\-_. ]", "_", safe_name)     # replace anything not alphanumeric, dash, underscore, dot, or space
safe_name = safe_name.replace(" ", "_")               # replace spaces with underscores

txt_path = os.path.join("out", f"item7_{safe_name}_{FISCAL_YEAR}.txt")

os.makedirs("out", exist_ok=True)

# Simple filename based on company + fiscal year

with open(txt_path, "w", encoding="utf-8") as f:
    f.write("Item 7 — Management’s Discussion and Analysis (MD&A)\n")
    f.write("="*70 + "\n\n")
    f.write(f"Company: {COMPANY_NAME}\n")
    f.write(f"CIK: {CIK}\n")
    f.write(f"Accession: {ACCESSION}\n")
    f.write(f"Report Date: {REPORT_DATE}\n")
    f.write(f"Filing Date: {FILING_DATE}\n")
    f.write("\n" + "="*70 + "\n\n")
    if item7_text:
        f.write(item7_text)
    else:
        f.write("<<Item 7 not found>>")

print(f"Done. TXT written: {txt_path}")
