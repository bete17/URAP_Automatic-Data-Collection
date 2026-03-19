import pandas as pd
import io
from prepare_companies import preparation

"""
Parses the LLM text and export to CSV according to template format
"""

class txtToCsv :

    def __init__(self, text : str, company : preparation, item : str) :
        self.text = text
        self.company = company
        self.item = item
        self.row_data = {
            'gvkey' : company.gvkey,
            'cik' : company.cik,
            'name' : company.name,
            'URL' : company.url,
        }
        self._parse_text_to_cells()

    def _parse_text_to_cells(self):
        lines = self.text.strip().split('\n')
        
        for line in lines:
            if '|' not in line:
                continue
                
            parts = [p.strip() for p in line.split('|')]
            question = parts[0]  # The first part is the header
            answers = parts[1:]  # Everything after the first pipe
            
            # If there's only one answer, just use the question as the header
            if len(answers) == 1:
                self.row_data[question] = answers[0]
            else:
                # If there are multiple answers, create unique headers:
                # e.g., "What savings... | 2000 | 1000" becomes 
                # "What savings..._1": 2000, "What savings..._2": 1000
                for i, answer in enumerate(answers, 1):
                    column_name = f"{question}_{i}"
                    self.row_data[column_name] = answer

    def to_df(self):
            # Create the DataFrame from the dictionary
            df = pd.DataFrame([self.row_data])
            
            # Transpose it: Columns become Rows, Rows become Columns
            df_transposed = df.T
            
            # Optional: Reset index so the 'Questions' are a proper column 
            # instead of just index labels
            df_transposed = df_transposed.reset_index()
            df_transposed.columns = ['Category', 'Value']
            
            return df_transposed
    
    def toCsv(self):
        df = self.to_df()
        corp = self.company
        # We use header=False because 'Category' and 'Value' 
        # are often not wanted in row-major research templates
        filename = f"{corp.gvkey}_{corp.fyear}_{self.item}.csv"
        df.to_csv(filename, index=False, header=False)
