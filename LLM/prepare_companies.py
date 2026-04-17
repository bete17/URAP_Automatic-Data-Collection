import pandas as pd
import os


"""
Grab all the necessary information from the CSV that contains the companies
"""

class preparation :
    item7_name : str
    item8_name : str
    gvkey : int
    fyear : int
    cik : int
    name : str
    fyearEnd : str
    index = 0
    numRows : int
    url : str

    """
    df.iat[r, c] -> return the value at (r, c)
    """

    def __init__(self, csvFileName : str, start = 1) : 
        """
        Takes in a csvFileName and a starting index (optional)
        Set up a pandas dataframe
        """
        main_path = os.path.join("..", "data", "sample_companies", csvFileName)
        meta_path = os.path.join("..", "data", "meta_data", "submission_info.csv")
        self.df = pd.read_csv(main_path)
        self.urlDf = pd.read_csv(meta_path)
        self.index = start
        self.numRows , _ = self.df.shape
        
    def getCompany(self, index : int) :
        """
        Sets all the instance variables
        Params: index: integer of index
        Returns: nothing
        """
        #Out of bounds check
        if(index > self.numRows - 1 or index < 0):
            raise ValueError("invalid index")
        self.index = index
        self.gvkey = self.df.iat[index, 0]
        self.cik = str(self.df.iat[index, 2]).zfill(10)
        self.fyear = int(self.df.iat[index, 5]) 
        self.corpName = self.df.iat[index, 1]
        self.name = f"{self.gvkey}_{self.fyear}"
        self.url = ""
        try: 
            self.url = self.getURL()
        except:
            self.url = ""

    def getURL(self) -> str:
        """
        Input: csvFileName containing the submission info
        Sets the self.url variable
        Returns: a string of the URL
        """
        self.urlDf = pd.read_csv(csvFileName)

        # Match on cik and fiscal_year
        match = self.urlDf[
            (self.urlDf['cik'] == int(self.cik)) &
            (self.urlDf['fiscal_year'] == self.fyear)
        ]

        if match.empty:
            raise ValueError(f"No URL found for CIK {self.cik}, fiscal year {self.fyear}")

        row = match.iloc[0]
        accession_clean = str(row['accession_number']).replace('-', '')
        primary_doc = str(row['primary_doc'])

        return (
            f"https://www.sec.gov/ix?doc=/Archives/edgar/data/"
            f"{int(self.cik)}/{accession_clean}/{primary_doc}"
        )

    def next(self) :
        #just incrementing
        self.index += 1
        self.getCompany(self.index)

    def getFileName(self) :
        return self.name


    #this method is for testing
    def __str__(self):
        return f"gvkey: {self.gvkey}, fyear: {self.fyear}, cik: {self.cik}"

