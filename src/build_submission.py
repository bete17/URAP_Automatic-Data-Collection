import zipfile
import re
import json
import pandas as pd


rows = []
    
sample = pd.read_csv("data/sample_all.csv", dtype={"cik": str})
sample = sample[sample['big05_rstr'] == True]
ciks_in_sample = sample['cik'].unique().tolist()


with zipfile.ZipFile("data/submissions.zip", "r") as z:
    count = 0
    stop = 5
    for name in z.namelist():
        # if count == stop:
        #     break
        if not name.endswith(".json"):
            continue
        
        with z.open(name) as f:
            data = json.load(f)
        
        match = re.search(r"CIK(\d{10})", name)
        if not match:
            continue
        cik = match.group(1)
        if cik not in ciks_in_sample:
            missing_cik.append(cik)
            continue
        # Decide how to access "recent" structure
        if "filings" in data and "recent" in data["filings"]:
            # main CIK submissions file
            recent = data["filings"]["recent"]
        else:
            # historical "submissions-YYYY" style file
            recent = data
        forms = recent.get("form", []) or []
        accession_numbers = recent.get("accessionNumber", []) or []
        primary_docs = recent.get("primaryDocument", []) or []
        r_date = recent.get("reportDate", []) or []
        
        for form, acc, primDoc, rep_date in zip(forms, accession_numbers, primary_docs, r_date):
            if form != "10-K":
                continue
            
            if not primDoc:
                primDoc = None
            
            if rep_date:
                try:
                    fiscal_year = int(rep_date[:4])
                except ValueError:
                    fiscal_year = None
            else:
                fiscal_year = None
            rows.append({
                "cik": cik,
                "accession_number": acc,
                "primary_doc": primDoc,
                "fiscal_year": fiscal_year
            })
        count += 1
            
df = pd.DataFrame(rows)
df.to_csv("data/submission_info.csv", index=False)
