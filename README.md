# Automating Data Collection
A Python project for extracting and analyzing restructuring-related disclosures from SEC 10-K filings.
This tool uses the EDGAR API to retrieve company filings, extract Item 7 (Management’s Discussion & Analysis) and Item 8 (Financial Statements), and filter for text specifically related to restructuring activities.

##🚀 Project Goals

Automatically fetch 10-K filings from the SEC’s EDGAR database.

Parse and isolate Item 7 and Item 8 sections.

Identify sentences discussing restructuring, realignment, severance, and related activities.

Output structured snippets for later testing against manually collected datasets.

Serve as a foundation for an NLP model to evaluate disclosure accuracy and completeness.

1. Obtain CIK with company name
2. Choose 10-k with CIK and Fiscal Year
3. fetch the html for the 10-k
4. convert html to text
5. extract item 7
6. write it out on a .txt file



IMPROVEMENT NEEDED NOT ALL TEST CASE WORK

If further work is to be done we need to set version control and redesign code in a OOP manner



Failed when there's more than one appearance of the subject title of item 7 


