import json
import os

from LLM import LLM
from prepare_companies import preparation
from Parse_LLM import Export
from jsonlToCsv import JsonlToCsv

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_HERE, "..", "data")
_EXPORT_DIR = os.path.join(_HERE, "..", "output")
_RESTRUCTURING_7 = os.path.join(_DATA_DIR, "item7_restructuring")
_RESTRUCTURING_8 = os.path.join(_DATA_DIR, "item8_restructuring")

# Where the JSONL files are stored (one file per item type).
OUTPUT_JSONL7 = os.path.join(_DATA_DIR, "item7_responses_all_sample.jsonl")
OUTPUT_JSONL8 = os.path.join(_DATA_DIR, "item8_responses_all_sample.jsonl")

# Limit how many rows to process in this run.
# Set to an int (e.g. 200) to cap the batch; set to None to process all rows.
MAX_ROWS: int | None = None


def _load_completed_keys(jsonl_path: str) -> set[tuple[str, str]]:
    """
    Each successful append writes one JSON object with ``name`` (gvkey_fyear) and ``item``
    (e.g. item7). Treat (name, item) as done so a restarted run skips those rows.
    """
    done: set[tuple[str, str, str]] = set()
    if not os.path.isfile(jsonl_path):
        return done
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            name = obj.get("name") + "_" + str(obj.get("fiscal_year"))
            item = obj.get("item")
            if name is not None and item is not None:
                done.add((str(name), str(item)))
    return done


def __main__():

    sample_csv = os.path.join(_DATA_DIR, "sample_collect_2025Fall.csv")
    prep = preparation(sample_csv)
    completed7 = _load_completed_keys(OUTPUT_JSONL7)
    completed8 = _load_completed_keys(OUTPUT_JSONL8)
    print(
        f"resume: {len(completed7)} item7 record(s) already in {os.path.basename(OUTPUT_JSONL7)} | "
        f"{len(completed8)} item8 record(s) already in {os.path.basename(OUTPUT_JSONL8)}"
    )

    end_index = prep.numRows if MAX_ROWS is None else min(prep.numRows, MAX_ROWS)
    for row_index in range(end_index):
        prep.getCompany(row_index)
        stem = prep.getFileName()
        item7_path = os.path.join(_RESTRUCTURING_7, f"{stem}_item7.txt")
        item8_path = os.path.join(_RESTRUCTURING_8, f"{stem}_item8.txt")
        name_key = str(prep.name)
        fyear = str(prep.fyear)

        print(f"row {row_index}/{prep.numRows - 1} {stem}")

        # --------------------
        # Item 7 (separate prompt instance)
        # --------------------
        item7_key = (name_key, "item7")
        if item7_key not in completed7:
            try:
                gpt7 = LLM(item7_path=item7_path)
                gpt7.getContent(7)
                txt7, _, _, _ = gpt7.push()
                Export(txt7, prep, "item7").append_to_jsonl(OUTPUT_JSONL7)
                completed7.add(item7_key)
            except Exception as e:
                print(f"ERROR item7 for {name_key}: {e!r}")

        # --------------------
        # Item 8 (separate prompt instance)
        # --------------------
        item8_key = (name_key, "item8")
        if item8_key not in completed8:
            try:
                gpt8 = LLM(item7_path=item7_path, item8_path=item8_path)
                gpt8.getContent(8)
                txt8, _, _, _ = gpt8.push()
                Export(txt8, prep, "item8").append_to_jsonl(OUTPUT_JSONL8)
                completed8.add(item8_key)
            except Exception as e:
                print(f"ERROR item8 for {name_key}: {e!r}")
    
    
    csv7 = JsonlToCsv(os.path.join(_DATA_DIR, "item7_responses_all_sample.jsonl"), os.path.join(_EXPORT_DIR, "item7"))
    csv8 = JsonlToCsv(os.path.join(_DATA_DIR, "item8_responses_all_sample.jsonl"), os.path.join(_EXPORT_DIR, "item8"))
    csv7.convert(overwrite=False)
    csv8.convert(overwrite=False)

__main__()

