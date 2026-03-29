import json
import os
import re
from typing import Any, Dict

import pandas as pd

from prepare_companies import preparation

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.abspath(os.path.join(_HERE, "..", "data"))
_DEFAULT_OUTPUT_PATH = os.path.join(_DATA_DIR, "llm_outputs.jsonl")

"""
Parses the LLM text and export to CSV according to template format
"""

class Export :

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

    def _build_responses(self) -> Dict[str, Any]:
        """
        Convert the flat `row_data` dict into a structured JSON-friendly form:
        - Single-answer questions become `responses[question] = "answer"`
        - Multi-answer questions become `responses[question] = ["a1", "a2", ...]`
        """
        base_fields = {"gvkey", "cik", "name", "URL"}
        responses: Dict[str, Any] = {}

        # Keys produced by _parse_text_to_cells look like: "<question>_<n>"
        # We'll group them back into "<question>" -> [answers...]
        multi_key_re = re.compile(r"^(.*)_([1-9][0-9]*)$")
        multi_groups: Dict[str, Dict[int, Any]] = {}
        singles: Dict[str, Any] = {}

        for key, value in self.row_data.items():
            if key in base_fields:
                continue

            m = multi_key_re.match(key)
            if not m:
                singles[key] = value
                continue

            question = m.group(1)
            idx = int(m.group(2))
            multi_groups.setdefault(question, {})[idx] = value

        # Finalize multi-answer groups
        for question, idx_map in multi_groups.items():
            ordered = [idx_map[i] for i in sorted(idx_map.keys())]
            responses[question] = ordered[0] if len(ordered) == 1 else ordered

        # Add single-answer questions
        responses.update(singles)
        return responses

    def to_json_record(self) -> Dict[str, Any]:
        """
        Build a single JSON object representing this company+item response.
        """
        corp = self.company
        return {
            "gvkey": corp.gvkey,
            "cik": corp.cik,
            "name": corp.name,
            "URL": corp.url,
            "item": self.item,
            "responses": self._build_responses(),
        }

    def append_to_jsonl(self, output_path: str = _DEFAULT_OUTPUT_PATH) -> None:
        """
        Append one JSON object per line (JSONL / NDJSON) to a single output file.

        This is robust for large batches because we avoid rewriting the whole file.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        record = self.to_json_record()
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")