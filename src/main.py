from filing import Extract_Filing
from items import Extract_Restructure
from savefile import FileExporter
import pandas as pd
import os
import glob
import argparse
import json
from datetime import datetime, timezone
from uuid import uuid4


def append_run_record(log_path, record):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=True) + "\n")


def classify_exception(exc):
    message = str(exc).lower()
    # If the error text suggests network/API issues, tag it for run-history summaries.
    if any(token in message for token in ("connect", "connection", "timeout", "api", "http")):
        return "api_connection_failed"
    return "unexpected_error"

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract restructuring text for a controlled subset of filings."
    )
    parser.add_argument(
        "-s", "--start-row",
        type=int,
        default=1,
        help="1-based row number in submission_info.csv to start from (default: 1).",
    )
    parser.add_argument(
        "-n", "--num-companies",
        type=int,
        default=None,
        help="Number of rows to go through (default: no limit).",
    )
    return parser.parse_args()

def main():
    args = parse_args()
    start_row = max(1, args.start_row)
    start_row_idx = start_row - 1
    num_companies = args.num_companies
    # Reject invalid CLI input early so the loop never runs with a nonsensical limit.
    if num_companies is not None and num_companies < 0:
        raise ValueError("--num-companies must be >= 0")

    # FILE PATHS AND USER AGENT
    submission_path = os.path.join("data", "meta_data", "submission_info.csv")
    sample_path = os.path.join("data", "sample_companies", "sample_all.csv")
    output_dir_7 = os.path.join("data", "testing_data", "Automatic", "item7_restructuring")
    output_dir_8 = os.path.join("data", "testing_data", "Automatic", "item8_restructuring")
    run_log_path = os.path.join("data", "error_log","run_history.jsonl")
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
    os.makedirs(os.path.dirname(run_log_path), exist_ok=True)

    # Only used to enforce --num-companies (same notion as former `total`).
    processed_for_limit = 0

    extractor = Extract_Restructure()
    run_id = str(uuid4())

    for idx, row in enumerate(submissions.itertuples(index=False)):
        # Skip rows before the user-selected start row (1-based CLI -> 0-based index).
        if idx < start_row_idx:
            continue
        # Stop once we've processed the requested number of valid submissions (if capped).
        if num_companies is not None and processed_for_limit >= num_companies:
            break

        #VARIABLES FOR THE CURRENT ROW
        cik = str(row.cik).zfill(10)
        year = row.fiscal_year
        primary_doc = getattr(row, "primary_doc", None)

        # Skip rows we cannot use: missing year, missing doc id, or placeholder "nan" text.
        if pd.isna(year) or not primary_doc or str(primary_doc).strip().lower() == "nan":
            continue

        year = int(year)
        processed_for_limit += 1

        # Resume behavior: if both output files already exist for this cik/year, skip.
        item7_existing = glob.glob(os.path.join(output_dir_7, f"*{cik}_{year}_item7.txt"))
        item8_existing = glob.glob(os.path.join(output_dir_8, f"*{cik}_{year}_item8.txt"))
        # Resume: both outputs already on disk for this CIK/year, so do not refetch.
        if item7_existing and item8_existing:
            append_run_record(
                run_log_path,
                {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "run_id": run_id,
                    "status": "skipped_existing_output",
                    "error_type": None,
                    "error_message": None,
                    "cik": cik,
                    "fiscal_year": year,
                    "item7_match_count": None,
                    "item8_match_count": None,
                },
            )
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
            # Empty fetch: nothing to parse; log and move on without raising.
            if not html:
                append_run_record(
                    run_log_path,
                    {
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "run_id": run_id,
                        "status": "failed",
                        "error_type": "missing_contents",
                        "error_message": "No HTML content returned from filing fetch.",
                        "cik": cik,
                        "fiscal_year": year,
                        "item7_match_count": 0,
                        "item8_match_count": 0,
                    },
                )
                continue

            sections = extractor.extract_items(html)
            item7_hits = extractor.capture_hits(sections.item7_blocks or [])
            item8_hits = extractor.capture_hits(sections.item8_blocks or [])
            item7_blocks_count = len(sections.item7_blocks or [])
            item8_blocks_count = len(sections.item8_blocks or [])
            item7_count = len(item7_hits or [])
            item8_count = len(item8_hits or [])

            # Classify outcome: no sections vs sections but no keyword hits vs OK.
            if item7_blocks_count == 0 and item8_blocks_count == 0:
                status = "failed"
                error_type = "missing_item_sections"
                error_message = "Unable to extract Item 7 or Item 8 sections."
            elif item7_count == 0 and item8_count == 0:
                status = "failed"
                error_type = "no_matching_keywords"
                error_message = "Item sections found, but no restructuring keywords matched."
            else:
                status = "success"
                error_type = None
                error_message = None

            exporter = FileExporter(output_dir_7=output_dir_7, output_dir_8=output_dir_8, cik=cik, year=year)
            exporter.save_restructuring(item7_hits=item7_hits, item8_hits=item8_hits)

            append_run_record(
                run_log_path,
                {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "run_id": run_id,
                    "status": status,
                    "error_type": error_type,
                    "error_message": error_message,
                    "cik": cik,
                    "fiscal_year": year,
                    "item7_match_count": item7_count,
                    "item8_match_count": item8_count,
                },
            )
        except Exception as e:
            print(f"[FAIL] cik={cik}, year={year}: {e}")
            append_run_record(
                run_log_path,
                {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "run_id": run_id,
                    "status": "failed",
                    "error_type": classify_exception(e),
                    "error_message": str(e),
                    "cik": cik,
                    "fiscal_year": year,
                    "item7_match_count": None,
                    "item8_match_count": None,
                },
            )

    # Summary line reflects whether the user capped how many companies to process.
    if num_companies is not None:
        print(f"Run window: start_row={start_row}, num_companies={num_companies}")
    else:
        print(f"Run window: start_row={start_row}, num_companies=ALL")

# Run as a script (not when imported as a module).
if __name__ == "__main__":
    main()
