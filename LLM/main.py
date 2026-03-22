import os

from LLM import LLM
from prepare_companies import preparation
from Parse_LLM import txtToCsv

_HERE = os.path.dirname(os.path.abspath(__file__))


def __main__() :

    prep = preparation("sample_collect_2025Fall.csv")
    prep.getCompany(104)
    stem = prep.getFileName()
    item7_path = os.path.join(_HERE, f"{stem}_item7.txt")

    print("parsing complete, pushing to LLM")
    gpt = LLM(item7_path=item7_path)
    gpt.getContent(7)
    txt = gpt.push()

    csv = txtToCsv(txt, prep, 'item7')
    csv.toCsv()

__main__()


