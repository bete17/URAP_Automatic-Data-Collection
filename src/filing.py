import requests
import re
import time
import pandas as pd

from dataclass import FilingMeta

# Intance variables
SEC_BASE = "https://data.sec.gov"
ARCHIVES_BASE = "https://www.sec.gov/Archives"
VALID_10K_FORMS = {"10-K", "10-k"}


class Extract_Filing:
    #Constructor
    def __init__(self, user_agent, cik, fiscal_year, company, submission_filepath, timeout=30, max_retries=3, retry_sleep=0.5):
        self.header = {"User-Agent": user_agent}
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_sleep = retry_sleep
        self.cik = str(int(cik)).zfill(10)
        self.submission_filepath = submission_filepath
        self.fiscal_year = int(fiscal_year)
        self.company = str(company)
    
    #call request with retry and timeout
    def request_web(self, url: str):
        last_exc = None
        for _ in range(self.max_retries):
            try:
                r = requests.get(url, headers=self.header, timeout=self.timeout)
                r.raise_for_status()
                return r
            except requests.RequestException as e:
                last_exc = e
                time.sleep(self.retry_sleep)
        raise last_exc
    
    @staticmethod
    def build_meta(
        company: str,
        cik: str,
        fiscal_year: int,
        form: str,
        accession: str,
        primary_doc: str,
        report_date: str,
    ) -> FilingMeta:
        acc_nodash = accession.replace("-", "")
        url = f"{ARCHIVES_BASE}/edgar/data/{int(cik)}/{acc_nodash}/{primary_doc}"
        return FilingMeta(
            company=company,
            cik=cik,
            fiscal_year=fiscal_year,
            form=form,
            accession=accession,
            primary_doc=primary_doc,
            report_date=report_date or None,
            url=url,
        )
    
    def get_submission(self) -> list[FilingMeta]:
        filepath = self.submission_filepath
        cik = self.cik
        fiscal_year = self.fiscal_year
        df = pd.read_csv(filepath, dtype={"cik": str})
        df = df[df['cik'] == cik]
        df = df[df['fiscal_year'] == fiscal_year] # what if none found?
        
        if df.empty:
            return None
        
        acc_no = df['accession_number'].values[0].replace("-", "")
        primary_doc = df['primary_doc'].values[0]
        return self.build_meta(
            company=self.company,
            cik=cik,
            fiscal_year=fiscal_year,
            form="10-K",
            accession=acc_no,
            primary_doc=primary_doc,
            report_date=fiscal_year,
        )
    
    def fetch_10k(self, meta: FilingMeta) -> str:
        r = self.request_web(meta.url)
        return r.text
                    
    def get_html(self) -> str | None:
        # 1) get submissions
        meta = self.get_submission()
        if not meta:
            return None
        # 3) fetch HTML
        html = self.fetch_10k(meta)
        return html
        


