from filing import Extract_Filing
from items import Extract_Restructure
from dataclass import FilingMeta
from bs4 import BeautifulSoup
import pandas as pd
import os

def main():
    
    
    filing = Extract_Filing(user_agent = "bruce0tan@gmail.com",cik ="0000001750", fiscal_year=2018, company="AIR", submission_filepath = "data/submission_info.csv")
    html = filing.get_html()
    item = Extract_Restructure()
    
    print(item.get_restructure(html))      
    
            

if __name__ == "__main__":
    main()
