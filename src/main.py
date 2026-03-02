from filing import Extract_Filing
from items import Extract_Restructure
from dataclass import FilingMeta
from bs4 import BeautifulSoup
import pandas as pd
import os

def main():
    

    filing = Extract_Filing("0000001750", fiscal_year=2018, company="AIR")
    html = filing.get_html()
    item = Extract_Restructure()
    
    print(item.get_restructure(html))
    
    # df = pd.read_csv("data/10k_filing_info.csv", dtype={"cik": str})
    # df2 = pd.read_csv("data/sample_all.csv", dtype={"cik": str})
    # df2 = df2[df2['big05_rstr'] == True]
    # ciks = df['cik'].unique().tolist()
    # ciks2 = df2['cik'].unique().tolist()
    # missing_ciks = []
    # for cik in ciks2:
    #     if cik not in ciks:
    #         missing_ciks.append(cik)
    # with open("data/missing_ciks.txt", "w") as f:
    #     for cik in missing_ciks:
    #         f.write(f"{cik}\n")
    
    # Separate item 7 and 8 restructure blocks
    # Write out 2 .txt files with a name gvkey_fyear_item7.txt and gvkey_fyear_item8.txt
    # Test out end to end process with a couple of rows from sample_all.csv
    # Add case when item 8 is on a different page
    
    # Things we need for fetching 10-k
    # accession number, cik, fiscal year (for matching), primary doc
    # For each submission file that matches CIK we extract the needed info
    # if its an extra submission file like Cik-submissions-001.json then we should hande it differently
                
    
            
            


if __name__ == "__main__":
    main()
