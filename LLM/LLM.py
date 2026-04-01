import os
import time
from typing import Optional

import ollama

_BASE = os.path.dirname(os.path.abspath(__file__))


class LLM:
    """Builds the prompt from Template.txt + restructuring files and calls Ollama.

    This class only **returns** model text from ``push()``; it does **not** persist outputs.
    Use ``Parse_LLM.Export`` (or similar) to save the response (CSV/JSON).
    """

    def __init__(
        self,
        item7_path: str,
        item8_path: Optional[str] = None,
        template_path: str = "Template.txt",
    ) -> None:
        """
        Args:
            item7_path: Filesystem path to the Item 7 restructuring text file.
            item8_path: Optional path to the Item 8 restructuring text file (required when using getContent(8)).
            template_path: Path to the question template; if relative, resolved next to this module.
        """
        self.item7_path = os.path.abspath(item7_path)
        self.item8_path = os.path.abspath(item8_path) if item8_path else None

        tmpl = template_path if os.path.isabs(template_path) else os.path.join(_BASE, template_path)
        with open(tmpl, "r", encoding="utf-8") as f:
            self.question = f.read()

        #under is for eval data
        self.token = 0
        self.question_completed: Optional[str] = None

    def getContent(self, item: int) -> str:
        """Append Item 7 or Item 8 restructuring text to the template prompt.

        Call at most one of ``getContent(7)`` or ``getContent(8)`` before ``push()`` if the
        model should see only that item’s text (calling both appends both bodies).
        """
        if item == 7:
            path = self.item7_path
        elif item == 8:
            if self.item8_path is None:
                raise ValueError("item8_path was not set; pass item8_path=... to the constructor.")
            path = self.item8_path
        else:
            raise ValueError(f"item must be 7 or 8, got {item!r}")

        with open(path, "r", encoding="utf-8") as g:
            body = g.read()
        
        self.question_completed = self.question + body
        return self.question_completed

    def push(self) -> str:
        if not self.question_completed:
            raise RuntimeError("Call getContent() before push().")
        start_time = time.time()
        response = ollama.generate(model="gpt-oss:20b",
                                   prompt=self.question_completed,
                                   options={"num_gpu": 99,
                                            "num_thread": 6,
                                            "num_ctx": 4096,
                                            "num_batch": 512,
                                            "num_predict":3000,
                                            "temperature": 0.1,
                                            "f16_kv": True,
                                            "think": False,
        }
    )
        end_time = time.time()
        time_taken = end_time - start_time
        #model_text = response["message"]["content"]
        model_text = response.response
        tokens = response.eval_count or 0
        #tokens_this_run = tokens-self.token
        self.token = tokens
        print(f"this process took {end_time - start_time:.2f} seconds")
        print(f"this process took {tokens} tokens")
        return model_text, tokens, time_taken, len(self.question_completed)
