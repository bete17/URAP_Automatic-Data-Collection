import os

from LLM import LLM
from prepare_companies import preparation
from Parse_LLM import Export

_HERE = os.path.dirname(os.path.abspath(__file__))

# Only one of Item 7 or Item 8 is sent to the model per run (not both).
ITEM = 7  # set to 8 to use Item 8 restructuring text only


def __main__() :

    sample_csv = os.path.join(_HERE, "..", "data", "sample_collect_2025Fall.csv")
    prep = preparation(sample_csv)
    prep.getCompany(104)
    stem = prep.getFileName()
    item7_path = os.path.join(_HERE, f"{stem}_item7.txt")
    item8_path = os.path.join(_HERE, f"{stem}_item8.txt")

    print("parsing complete, pushing to LLM")
    gpt = LLM(
        item7_path=item7_path,
        item8_path=item8_path if ITEM == 8 else None,
    )
    gpt.getContent(ITEM)
    txt = gpt.push()

    exporter = Export(txt, prep, f"item{ITEM}")
    exporter.append_to_jsonl()

__main__()


