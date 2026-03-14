from LLM import LLM
from prepare_companies import preparation
from csvConvert import txtToCsv

def __main__() :

    prep = preparation("sample_collect_2025Fall.csv")
    prep.getCompany(104)
    fileName = prep.getFileName()
    

    print("parsing complete, pushing to LLM")
    gpt = LLM()
    gpt.getFileName(fileName)
    gpt.getContent(7)
    txt = gpt.push()

    csv = txtToCsv(txt, prep, 'item7')
    csv.toCsv()

__main__()



