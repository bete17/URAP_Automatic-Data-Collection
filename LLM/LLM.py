import ollama 
import time

class LLM:

    def __init__(self) :
        self.item7 = "_item7.txt"
        self.item8 = "_item8.txt"
        with open("Question.txt", "r", encoding="utf-8") as f:
            self.question = f.read()

    def getFileName(self, name: str) :
        #To get the filename contains the segments
        self.item7 = name + self.item7 
        self.item8 = name + self.item8 

    def getContent(self, item : int) :
        #Append the item7/8 to the question doc and change it to a string
        if item == 7:
            name = self.item7
        elif item == 8:
            name = self.item8
        with open(name, "r", encoding = "utf-8") as g:
            item7 = g.read()
        self.question = self.question + item7
        return self.question 

    def push(self) :
        #push to LLM
        start_time = time.time()
        response = ollama.chat(model="gpt-oss:20b", messages = 
                       [{'role' : 'user', 'content' : self.question}])
        model_text = response['message']['content']
        end_time = time.time()
        time_taken = end_time - start_time
        print(f"this process took {time_taken} seconds")
        return model_text
        
    