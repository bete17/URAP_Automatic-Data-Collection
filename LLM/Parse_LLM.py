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
QUESTION_KEYS = [
    "announcement_date",
    "stated_reasons",
    "anticipated_savings",
    "prior_year_savings",
    "restructuring_charges",
    "employee_reduction",
    "facility_closures",
    "facilities_closed",
    "cost_reduction_mentioned",
    "completion_timeline_reported",
    ]
class Export :

    def __init__(self, text : str, company : preparation, item : str) :
        self.text = text
        self.company = company
        self.item = item
        self.row_data = {
            'gvkey' : company.gvkey,
            'cik' : company.cik,
            'name' : company.name,
            'fiscal_year': company.fyear,
            'URL' : company.url,
        }
        self._parse_text_to_cells() 


    def _parse_text_to_cells(self):
        """
        Convert the llm reply string into key/valued entries
        Params:
            - text: The llm reply string
        Returns:
            None
        """
        lines = [l.strip() for l in self.text.strip().split('\n') if l.strip()]

        parsed = 0
        for line in lines:
            if parsed >= len(QUESTION_KEYS):
                break
            if '|' not in line:
                continue  # skip preamble/blank lines

            parts = [p.strip() for p in line.split('|')]

            # Handle both "question | answer" and "answer1 | answer2" formats
            # If first part is long (>50 chars), treat it as the question label and skip it
            if len(parts[0]) > 50:
                answers = parts[1:]
            else:
                answers = parts

            if not answers:
                continue

            key = QUESTION_KEYS[parsed]
            if len(answers) == 1:
                self.row_data[key] = answers[0]
            else:
                for j, answer in enumerate(answers, 1):
                    self.row_data[f"{key}_{j}"] = answer

            parsed += 1

    def _build_responses(self) -> Dict[str, Any]:
        """
        Build the dictionary of the LLM responses
        Params:
            - None
        Returns:
            - responses: A dictionary of the responses
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
        Put together the JSON record for a company+item response
        Params:
            - None
        Returns:
            - record: A dictionary of the record
        """
        corp = self.company
        return {
            "gvkey": str(corp.gvkey),
            "cik": str(corp.cik),
            "name": corp.corpName,
            "fiscal_year": int(corp.fyear),
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