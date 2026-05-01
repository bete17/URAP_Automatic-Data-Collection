Requirements:
1. Have Ollama installed on your system
2. Have "gpt-oss:20b" model installed on ollama
    a. If you want to use another model of your choice, go into push() function in LLM.py 
        and find the line "response = ollama.generate", in the generate loop, change the 
        model parameter. 
    b. if the model is not taking all the information, change "num_ctx" to a bigger number
    c. If the model is not outputting/cuts off, change "num_predict" to a bigger number

How to use it:
  1. have a txt file with the name formatted as f"{gvkey}_{fyear}_item{#}.txt"
  2. ensure all item7 text files are in the /data/testing_data/item7
  3. ensure all item8 text files are in the /data/testing_data/item8
  4. then run main.py with ollama open
  5. All the exports should be in a folder "output"
