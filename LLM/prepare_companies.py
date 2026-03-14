import pandas as pd


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
    ARCHIVES_BASE = "https://www.sec.gov/Archives"

    """
    df.iat[r, c] -> return the value at (r, c)
    """

    def __init__(self, csvFileName : str, start = 1) : 
        """
        Takes in a csvFileName and a starting index (optional)
        Set up a pandas dataframe
        """
        self.df = pd.read_csv(csvFileName)
        self.index = start
        self.numRows , _ = self.df.shape
        
    def getCompany(self, index : int) :
        """
        Sets all the instance variables
        Params: index: integer of index
        Returns: nothing
        """
        if(index > self.numRows - 1 or index < 0):
            raise ValueError("invalid index")
        self.index = index
        self.gvkey = self.df.iat[index, 0]
        self.name = self.df.iat[index, 1]
        self.cik = self.df.iat[index, 3]
        self.cik = self.df.iat[index, 4]
        self.fyear = self.df.iat[index, 5]
        self.name = f"{self.gvkey}_{self.fyear}"
        self.url = ""


    def next(self) :
        #just incrementing
        self.index += 1
        self.getCompany(self.index)

    def getFileName(self) :
        return self.name


    #this method is for testing
    def __str__(self):
        return f"gvkey: {self.gvkey}, name: {self.name}"


