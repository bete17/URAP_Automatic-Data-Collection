import json
import os

from LLM import LLM
from prepare_companies import preparation
from Parse_LLM import Export

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_HERE, "..", "data")

# Only one of Item 7 or Item 8 is sent to the model per run (not both).
ITEM = 7  # set to 8 to use Item 8 restructuring text only

# Where the JSONL files are stored
# Placeholder — replace `[filepath]` with your real output basename when ready (e.g. "llm_outputs.jsonl").
OUTPUT_JSONL7 = os.path.join(_DATA_DIR, "[filepath].jsonl")
OUTPUT_JSONL8 = os.path.join(_DATA_DIR, "[filepath].jsonl")


def _load_completed_keys(jsonl_path: str) -> set[tuple[str, str]]:
    """
    Each successful append writes one JSON object with ``name`` (gvkey_fyear) and ``item``
    (e.g. item7). Treat (name, item) as done so a restarted run skips those rows.
    """
    done: set[tuple[str, str]] = set()
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
            name = obj.get("name")
            item = obj.get("item")
            if name is not None and item is not None:
                done.add((str(name), str(item)))
    return done


def __main__():

    sample_csv = os.path.join(_DATA_DIR, "sample_collect_2025Fall.csv")
    prep = preparation(sample_csv)
    item_label = f"item{ITEM}"
    completed = _load_completed_keys(OUTPUT_JSONL)
    print(f"resume: {len(completed)} record(s) already in {os.path.basename(OUTPUT_JSONL)}")

    for row_index in range(prep.numRows):
        prep.getCompany(row_index)
        stem = prep.getFileName()
        item7_path = os.path.join(_HERE, f"{stem}_item7.txt")
        item8_path = os.path.join(_HERE, f"{stem}_item8.txt")

        if (str(prep.name), item_label) in completed:
            print(f"skip (already done) row {row_index}/{prep.numRows - 1} {stem}")
            continue

        print(f"row {row_index}/{prep.numRows - 1} {stem}")
        gpt = LLM(
            item7_path=item7_path,
            item8_path=item8_path if ITEM == 8 else None,
        )
        # Prepare the prompt
        gpt.getContent(ITEM)
        txt = gpt.push()
        # Export the response
        exporter = Export(txt, prep, item_label)
        exporter.append_to_jsonl(OUTPUT_JSONL)
        # Add it the records of the completed items
        completed.add((str(prep.name), item_label))

        # Item 8 output
        gpt.getContent(8)
        txt = gpt.push()
        exporter = Export(txt, prep, item_label)
        exporter.append_to_jsonl(OUTPUT_JSONL8)
        completed.add((str(prep.name), item_label))


__main__()

