# Project Description
We want to collect data of 20,000+ companies and we need to automate that process instead of manually collecting it. We can use the SEC API to obtain our 10-k files and then run it through an algorithm that captures restructuring related information. With these information we will feed it to an LLM and then use the LLM to answer our list of questions and that will be our final complete data set.

## Data
All the data that is either used for testing or querying.

sample_all.csv : All the desired companies that we want to collect.

sample_collect_2025Fall.csv : All the companies that we manually collected (just 50 of them from top to bottom).

submissions_info : This is where we store all the companies meta data needed to build each 10-k URL. This can be build with the build_filling.py in SRC. 

The file above is needed for better run time in getting the 10-k.

## SRC
dataclasses.py :	Holds an instance of classes like items, block (paragraphs) and Filing meta data. 

filing.py	: Fetch the 10k File.

items.py : Fetch item 7 & 8 and extract from each the restructuring information.

main.py : To pilot the code and build our final dataset.

## Testing
test_filing : Verify that we have the right 10-k.

test_item : Verify that we have the right item 7 and 8.

test_restructuring : Compare the results between our manual collection and automatic collection.

test_LLM : verify the results of the LLM and our manual answers.

