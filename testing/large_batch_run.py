import os
import sys
import time
import pandas as pd
from bs4 import BeautifulSoup
import re

# Add src/ to Python path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(ROOT, "src"))

from filing import Extract_Filing


DATA_PATH = os.path.join(ROOT, "data", "sample_collect_2025Fall.csv")
FAILURES_PATH = os.path.join(ROOT, "data", "large_batch_failures.csv")


def validate_10k_html(html: str) -> bool:
    lower = html.lower()
    if len(lower) < 5000:
        return False  # too small to be a full 10-K
    return True

def main(max_rows=None):

    # ------------------------
    # Load CSV with pandas
    # ------------------------
    df = pd.read_csv(DATA_PATH)

    # choose only big05_rstr == True
    df = df[df['big05_rstr'] == True]
    
    if max_rows:
        df = df.iloc[:max_rows]

    total = len(df)
    missing_values = 0
    successes = 0
    failure_records = []

    start = time.perf_counter()

    for idx, row in df.iterrows():
        cik = row["cik"]
        
        if cik is None or pd.isna(cik):
            missing_values += 1
            failure_records.append((cik, "missing_cik"))
            continue
        
        cik = extractor.cik  # zero-padded
        company = row.get("conm", "")
        f_year = row.get("fyear")
        
        extractor = Extract_Filing(cik, f_year, company)

        row_start = time.perf_counter()
        

        try:
            fiscal_year = int(fiscal_year)
        except:
            failure_records.append((cik, "invalid_fiscal_year"))
            continue

        # --- step 1: get submissions ---
        try:
            subs = extractor.get_submissions()
        except Exception as e:
            failure_records.append((cik, f"get_submissions:{repr(e)}"))
            continue

        # --- step 2: choose 10-K ---
        try:
            meta = extractor.choose_10k(company, subs)
        except Exception as e:
            failure_records.append((cik, f"choose_10k:{repr(e)}"))
            continue

        if meta is None:
            failure_records.append((cik, "no_10k_for_year"))
            
            if len(failure_records) <= 5: 
                extractor.debug_print_all_10ks(subs)

            continue

        # --- step 3: fetch html ---
        try:
            html = extractor.fetch_10k(meta)
        except Exception as e:
            failure_records.append((cik, f"fetch_10k:{repr(e)}"))
            continue

        # --- step 4: validation ---
        if not validate_10k_html(html):
            failure_records.append((cik, "html_validation_failed"))
            continue
        
        if idx % 10 == 0:
            time.sleep(0.1)


        # Success
        successes += 1
        elapsed = time.perf_counter() - row_start

        # Respectful delay

    # Summary
    total_time = time.perf_counter() - start
    print("\n"+DATA_PATH)
    print("\n========= SUMMARY =========")
    print(f"Total processed: {total}")
    print(f"Successes:       {successes}")
    print(f"Failures:        {len(failure_records)}")
    print(f"Success rate:    {successes/total*100:.2f}%")
    print(f"Avg per CIK:     {total_time/total:.2f}s")
    print(f"Total time:      {total_time/60:.1f} minutes")

    # Save failures
    failures_df = pd.DataFrame(failure_records, columns=["CIK", "reason"])
    failures_df.to_csv(FAILURES_PATH, index=False)
    print(f"Saved failure log : {FAILURES_PATH}")


if __name__ == "__main__":
    # during development, limit to maybe 100 rows
    main(max_rows=51)

    # for full production run:
    # main(max_rows=None)
