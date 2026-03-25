import os

from LLM import LLM
from prepare_companies import preparation
from Parse_LLM import Export

_HERE = os.path.dirname(os.path.abspath(__file__))


def __main__() :

    sample_csv = os.path.join(_HERE, "..", "data", "sample_collect_2025Fall.csv")
    prep = preparation(sample_csv)
    prep.getCompany(104)
    stem = prep.getFileName()
    item7_path = os.path.join(_HERE, f"{stem}_item7.txt")
    item8_path = os.path.join(_HERE, f"{stem}_item8.txt")

    print("parsing complete, pushing to LLM")
    gpt = LLM(item7_path=item7_path, item8_path=item8_path)
    gpt.getContent(7)
    gpt.getContent(8)
    txt = gpt.push()

    exporter = Export(txt, prep, 'item7')
    exporter.append_to_jsonl()

__main__()


