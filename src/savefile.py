import os
import csv

class FileExporter:
    def __init__(self, output_dir, cik, year):
        self.output_dir = output_dir
        self.cik = cik
        self.year = year

    def get_gvkey(self):
        """Get the gvkey for the given cik and year from sample_all.csv

        Returns:
            str: The gvkey corresponding to the given cik and year
        """

        return None
    
    def save_restructuring(self, item7_hits, item8_hits):
        """Save the restructuring-blocks in files in [txt] format for item 7 and item 8 respectively

        Args:
            hits (List[Block]): Restructuring-related blocks
            filepath7 (str): Path to the output file for item 7
            filepath8 (str): Path to the output file for item 8

        Returns:
            None
        """

        return None
    
    def save_llm_output(self, llm_output7, llm_output8):
        """Save the LLM output in a file in a csv format

        Args:
            llm_output7 (str): The output from the LLM for item 7
            llm_output8 (str): The output from the LLM for item 8
            filepath (str): Path to the output file

        Returns:
            None
        """

        return None