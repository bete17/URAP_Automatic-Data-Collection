from Extract_File import Extractor
from Extract_Items import ItemExtractor
from dataclass import FilingMeta
from bs4 import BeautifulSoup

def main():
    # --- Define metadata for one known 10-K ---
    meta = FilingMeta(
        company="AIR",
        cik="0000001750",
        fiscal_year=2019,
        form="10-K",
        accession="0001047469-19-004266",
        primary_doc="a2239223z10-k.htm",
        report_date="2019-05-31",
        url="https://www.sec.gov/Archives/edgar/data/1750/000104746919004266/a2239223z10-k.htm"
    )

    # --- Fetch HTML from SEC ---
    extractor = Extractor()
    html = extractor.fetch_10k(meta)
    


if __name__ == "__main__":
    main()
