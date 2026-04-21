from filing import Extract_Filing
from items import Extract_Restructure
from savefile import FileExporter
import pandas as pd
import os
import glob

def main():
    # FILE PATHS AND USER AGENT #
    submission_path = os.path.join("data", "meta_data", "submission_info.csv")
    sample_path = os.path.join("data", "sample_companies", "sample_all.csv")
    output_dir_7 = os.path.join("data", "testing_data", "Automatic", "item7_restructuring")
    output_dir_8 = os.path.join("data", "testing_data", "Automatic", "item8_restructuring")
    user_agent = os.getenv("SEC_USER_AGENT", "bruce0tan@gmail.com")

    submissions = pd.read_csv(submission_path, dtype={"cik": str})
    samples = pd.read_csv(sample_path, dtype={"cik": str})

    # Standardize keys for robust matching.
    submissions["cik"] = submissions["cik"].astype(str).str.zfill(10)
    submissions["fiscal_year"] = pd.to_numeric(submissions["fiscal_year"], errors="coerce").astype("Int64")
    samples["cik"] = samples["cik"].astype(str).str.zfill(10)
    samples["fyear"] = pd.to_numeric(samples["fyear"], errors="coerce").astype("Int64")

    # Company lookup used for metadata in Extract_Filing.
    company_lookup = (
        samples.dropna(subset=["fyear"])
        .drop_duplicates(subset=["cik", "fyear"])
        .set_index(["cik", "fyear"])["conm"]
        .to_dict()
    )

    os.makedirs(output_dir_7, exist_ok=True)
    os.makedirs(output_dir_8, exist_ok=True)

    total = 0
    skipped = 0
    success = 0
    failed = 0

    extractor = Extract_Restructure()

    for row in submissions.itertuples(index=False):
        cik = str(row.cik).zfill(10)
        year = row.fiscal_year
        primary_doc = getattr(row, "primary_doc", None)

        if pd.isna(year) or not primary_doc or str(primary_doc).strip().lower() == "nan":
            continue

        year = int(year)
        total += 1

        # Resume behavior: if both output files already exist for this cik/year, skip.
        item7_existing = glob.glob(os.path.join(output_dir_7, f"*{cik}_{year}_item7.txt"))
        item8_existing = glob.glob(os.path.join(output_dir_8, f"*{cik}_{year}_item8.txt"))
        if item7_existing and item8_existing:
            skipped += 1
            continue

        company = company_lookup.get((cik, year), cik)
        filing = Extract_Filing(
            user_agent=user_agent,
            cik=cik,
            fiscal_year=year,
            company=company,
        )

        try:
            html = filing.get_html(submission_path)
            if not html:
                failed += 1
                continue

            sections = extractor.extract_items(html)
            item7_hits = extractor.capture_hits(sections.item7_blocks or [])
            item8_hits = extractor.capture_hits(sections.item8_blocks or [])

            exporter = FileExporter(output_dir_7=output_dir_7, output_dir_8=output_dir_8, cik=cik, year=year)
            exporter.save_restructuring(item7_hits=item7_hits, item8_hits=item8_hits)
            success += 1
        except Exception as e:
            failed += 1
            print(f"[FAIL] cik={cik}, year={year}: {e}")

    print(f"Processed: {total}")
    print(f"Skipped (already collected): {skipped}")
    print(f"Succeeded: {success}")
    print(f"Failed: {failed}")

if __name__ == "__main__":
    main()
