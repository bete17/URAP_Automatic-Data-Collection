import requests
import re
import os
import time
from bs4 import BeautifulSoup

from dataclass import FilingMeta, ItemSections


#URLS
SEC_BASE = "https://data.sec.gov"
ARCHIVES_BASE = "https://www.sec.gov/Archives"

class Extractor:
    def __init__(self, timeout = 30, max_retries = 3, retry_sleep = 0.5):
        self.header = {"User-Agent": "brucetan@berkeley.edu"}
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_sleep = retry_sleep
    
    @staticmethod
    def clean_name(s: str) -> str:
        s = s.lower().strip()
        s = re.sub(r'[,.\-&/]+', ' ', s)   # remove punctuation
        s = re.sub(r'\b(incorporated|inc|corp|corporation|co|ltd|plc|llc|holdings?|group)\b', '', s) # drop suffixes
        s = re.sub(r'\s+', ' ', s)         # collapse extra spaces
        return s.strip()
        
    # ---------- 1) company -> CIK ----------    
    def get_cik(self, company_name : str):
        url = SEC_BASE + "/files/company_tickers.json"
        r = requests.get(url,headers= self.header)
        r.raise_for_status()
        data = r.json()
        
        mapping = {}
        
        for rec in data.values():
            cik = str(rec["cik_str"]).zfill(10)
            title = Extractor.clean_name(rec["title"])
            mapping[title] = cik
        
        norm = Extractor.clean_name(company_name)
        return mapping.get(norm)
        
    # ---------- 2) CIK -> submissions ----------
    def get_submissions(self, cik : str) -> dict:
    #Fetch the SEC submission for a company cik
        url = f"{SEC_BASE}/submissions/CIK{str(int(cik)).zfill(10)}.json"
        r = requests.get(url, headers=self.header, timeout=30)
        r.raise_for_status()
        return r.json()
    
    # ---------- 3) choose 10-K for fiscal year ----------
    def choose_10k(self,company : str, submissions: dict, fiscal_year: int) -> dict:
        #get the first 10k dict macthing the fiscal year
        recent = submissions.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        accessions = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])
        report_dates = recent.get("reportDate", [])
        filing_dates = recent.get("filingDate", [])
        
        def ok(form: str) -> bool:
            f = (form or "").upper()
            if f == "10-K":
                return True
            if f == "10-K/A":
                return include_amendments
            return False
        
        # First pass: prefer reportDate match (when present)
        for form, acc, doc, rdate, fdate in zip(forms, accessions, primary_docs, report_dates, filing_dates):
            if ok(form) and rdate and str(rdate).startswith(str(fiscal_year)):
                return self._build_meta(company, self.cik, fiscal_year, form, acc, doc, rdate, fdate)

        # Fallback: filingDate match
        for form, acc, doc, rdate, fdate in zip(forms, accessions, primary_docs, report_dates, filing_dates):
            if ok(form) and fdate and str(fdate).startswith(str(fiscal_year)):
                return self._build_meta(company, cik, fiscal_year, form, acc, doc, rdate, fdate)

        return None
    
    @staticmethod
    def _build_meta(company: str, cik: str, fiscal_year: int, form: str, accession: str, primary_doc: str,
                    report_date: str, filing_date: str) -> FilingMeta:
        is_amend = form.upper() == "10-K/A"
        acc_nodash = accession.replace("-", "")
        url = f"{ARCHIVES_BASE}/edgar/data/{int(cik)}/{acc_nodash}/{primary_doc}"
        return FilingMeta(
            company=company,
            cik=str(cik).zfill(10),
            fiscal_year=fiscal_year,
            form=form,
            accession=accession,
            primary_doc=primary_doc,
            report_date=report_date or None,
            filing_date=filing_date or None,
            url=url,
            is_amendment=is_amend
        )
    
     # 4) fetch HTML ----------
    def fetch_10k(self, meta: FilingMeta) -> str:
        """
        Fetch the HTML at meta.url.
        If the response is an index page, you'll resolve it later (next step in your pipeline).
        """
        last_err = None
        for _ in range(self.max_retries):
            try:
                r = requests.get(meta.url, headers=self.headers, timeout=self.timeout)
                r.raise_for_status()
                return r.text
            except Exception as e:
                last_err = e
                time.sleep(self.retry_sleep)
        # bubble up the last error after retries
        raise last_err
    
    def fetch_item7(self, tenK):
        return 0
    