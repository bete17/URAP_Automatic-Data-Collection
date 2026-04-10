"""
jsonl_to_csv.py
---------------
Reads a .jsonl file and writes one CSV per line using pandas.

Output filename : {gvkey}_{fiscal_year}_{item}.csv
Output directory: set OUTPUT_DIR below, or pass as command-line args.

Usage
-----
    python jsonl_to_csv.py                          # uses defaults below
    python jsonl_to_csv.py data.jsonl /path/to/out  # explicit args
"""

import json
import os
import sys

import pandas as pd

# Configuration

INPUT_FILE = "data.jsonl"       # relative to this script's directory
OUTPUT_DIR = "/tmp/csv_output"  # must differ from the script's directory

# Core class

class JsonlToCsv:
    def __init__(self, input_file: str, output_dir: str):
        self.input_path = self._resolve_input(input_file)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    # public

    def convert(self, overwrite: bool = True) -> None:
        """
        Process every line in the JSONL file.

        overwrite=True  -> write all CSVs, replacing any existing files.
        overwrite=False -> skip lines whose output CSV already exists.
        """
        processed, skipped, existing = 0, 0, 0

        with open(self.input_path, "r", encoding="utf-8") as fh:
            for line_num, raw in enumerate(fh, start=1):
                raw = raw.strip()
                if not raw:
                    continue

                try:
                    record = json.loads(raw)
                except json.JSONDecodeError as exc:
                    print(f"  [line {line_num}] JSON parse error - skipping. ({exc})")
                    skipped += 1
                    continue

                try:
                    if not overwrite and self._output_exists(record):
                        filename = self._build_filename(record)
                        print(f"  [line {line_num}] Already exists, skipping -> {filename}")
                        existing += 1
                        continue

                    filepath = self._write_csv(record)
                    print(f"  [line {line_num}] -> {filepath}")
                    processed += 1
                except (KeyError, ValueError) as exc:
                    print(f"  [line {line_num}] Skipped - {exc}")
                    skipped += 1

        print(f"\nDone. {processed} CSV(s) written, {existing} skipped (already exist), {skipped} error(s).")
        print(f"Output directory: {self.output_dir}")

    # private

    def _build_filename(self, record: dict) -> str:
        """Return the output CSV filename for a record."""
        gvkey = record.get("gvkey")
        if not gvkey:
            raise ValueError("missing 'gvkey'")

        fiscal_year = record.get("fiscal_year") or record.get("responses", {}).get("fiscal_year")
        if not fiscal_year:
            raise ValueError("missing 'fiscal_year'")

        item = record.get("item", "")
        return f"{gvkey}_{fiscal_year}_{item}.csv" if item else f"{gvkey}_{fiscal_year}.csv"

    def _output_exists(self, record: dict) -> bool:
        """Return True if the output CSV for this record already exists."""
        filename = self._build_filename(record)
        return os.path.isfile(os.path.join(self.output_dir, filename))

    def _write_csv(self, record: dict) -> str:
        """Flatten one record into a DataFrame and save it as a CSV."""
        df = self._to_dataframe(record)
        filename = self._build_filename(record)
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False)
        return filepath

    def _to_dataframe(self, record: dict) -> pd.DataFrame:
        """
        Build a DataFrame with a 'field' column and one or more value columns.

        - Scalar / dict values  -> single 'value' column
        - List values           -> value, value_1, value_2, ...

        Top-level fields come first; responses sub-keys follow without prefix.
        Keys already emitted at the top level are skipped in the responses block
        to avoid duplicates (e.g. fiscal_year appears in both).
        """
        rows = []
        top_level_keys = set()

        for key, val in record.items():
            if key == "responses" and isinstance(val, dict):
                continue
            rows.append(self._make_row(key, val))
            top_level_keys.add(key)

        responses = record.get("responses")
        if isinstance(responses, dict):
            for sub_key, sub_val in responses.items():
                if sub_key in top_level_keys:
                    continue
                rows.append(self._make_row(sub_key, sub_val))

        df = pd.DataFrame(rows).fillna("")

        value_cols = sorted(
            [c for c in df.columns if c.startswith("value_")],
            key=lambda c: int(c.split("_")[1]),
        )
        base_cols = ["field"] + (["value"] if "value" in df.columns else [])
        return df[base_cols + value_cols]

    @staticmethod
    def _make_row(field: str, val) -> dict:
        """
        Return a dict representing one CSV row.
        Lists -> first item in 'value', remaining in value_1, value_2, ...
        Everything else -> {field, value}

        If the first element of a list is a question string (ends with '?'),
        it is a prompt/header artifact and is dropped.
        """
        if isinstance(val, list):
            items = val[1:] if val and isinstance(val[0], str) and val[0].strip().endswith("?") else val
            row = {"field": field, "value": JsonlToCsv._flatten(items[0])} if items else {"field": field}
            for i, item in enumerate(items[1:], start=1):
                row[f"value_{i}"] = JsonlToCsv._flatten(item)
            return row
        return {"field": field, "value": JsonlToCsv._flatten(val)}

    @staticmethod
    def _flatten(val) -> str:
        """Recursively flatten lists/dicts into a readable string."""
        if isinstance(val, list):
            return " | ".join(JsonlToCsv._flatten(v) for v in val)
        if isinstance(val, dict):
            return "; ".join(f"{k}: {JsonlToCsv._flatten(v)}" for k, v in val.items())
        return str(val)

    @staticmethod
    def _resolve_input(input_file: str) -> str:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = input_file if os.path.isabs(input_file) else os.path.join(script_dir, input_file)
        if not os.path.isfile(path):
            sys.exit(f"Error: input file not found -> {path}")
        return path


# Entry point

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    output_dir = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_DIR

    converter = JsonlToCsv(input_file, output_dir)
    converter.convert()


if __name__ == "__main__":
    main()