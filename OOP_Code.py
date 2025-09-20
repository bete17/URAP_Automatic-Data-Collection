import requests
import re
from bs4 import BeautifulSoup
import os

#URLS
SEC_BASE = "https://data.sec.gov"
ARCHIVES_BASE = "https://www.sec.gov/Archives"
USER_AGENT = os.environ.get("SEC_USER_AGENT", "Your Name your@email")
headers = {"User-Agent": "brucetan@berkeley.edu"}

class Extractor:
    def __init__(self):
        self.cik = ""
        self.accession = ""
        self.primary_doc = ""
        self.reporting_date = ""
    
    def clean_name(s: str) -> str:
        s = s.lower().strip()
        s = re.sub(r'[,.\-&/]+', ' ', s)   # remove punctuation
        s = re.sub(r'\b(incorporated|inc|corp|corporation|co|ltd|plc|llc|holdings?|group)\b', '', s) # drop suffixes
        s = re.sub(r'\s+', ' ', s)         # collapse extra spaces
        return s.strip()
        
        
    def get_cik(self, company_name : str):
        url = SEC_BASE + "/files/company_tickers.json"
        
        r = requests.get(url,headers=HEADERS)
        r.raise_for_status()
        data = r.json()
        
        mapping = {}
        
        for rec in data.values():
            cik = str(rec["cik_str"]).zfill(10)
            title = Extractor.clean_name(rec["title"])
            mapping[title] = cik
        
        norm = Extractor.clean_name(company_name)
        self.cik = mapping.get(norm)
        
    
    def get_submissions(self) -> dict:
    #Fetch the SEC submission for a company cik
        url = f"{SEC_BASE}/submissions/CIK{str(int(self.cik)).zfill(10)}.json"
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.json()
    
    def choose_10k(self, submissions: dict, fiscal_year: int) -> dict:
        #get the first 10k dict macthing the fiscal year
        recent = submissions.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        self.accessions = recent.get("accessionNumber", [])
        self.primary_docs = recent.get("primaryDocument", [])
        self.report_dates = recent.get("reportDate", [])
        self.filing_dates = recent.get("filingDate", [])
        
        for form, acc, doc, rdate, fdate in zip(forms, accessions, primary_docs, report_dates, filing_dates):
            if form.upper() == "10-K" and rdate and rdate.startswith(str(fiscal_year)):
                return {
                "accession": acc,
                "primary_doc": doc,
                "report_date": rdate,
                "filing_date": fdate
            }
        return None
    
    def build_10k_url(self) -> str:
        acc_no_dashes = self.accession.replace("-", "")
        base = f"{SEC_BASE}/Archives/edgar/data/{int(self.cik)}/{acc_no_dashes}"
        return f"{base}/{self.primary_doc}"
    
    def fetch_10k()