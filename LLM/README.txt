Instructions:
1. Ollama installation:
    -> This program uses Ollama to connect with LLM.
    -> The model this program uses is the "GPT-OSS: 20B" model, which can be downloaded at:
        http://ollama.com/library/gpt-oss:20b
    -> If you want to use any other model, go to push() function in LLM.py and change the model parameter in 
        ollama.generate() to the desired model.
    -> Ollama has to be open in the background when using this script
2. Ensure the corresponding item7 and item8 .txt files are in /../data/testing_data/item{#}, and with all the file being 
    named following the {gvkey}_{fiscal_year}_item{#}.txt convention. 

