import os
import csv
from typing import List
from dataclass import FilingMeta


class FileExporter:

    def __init__(self, output_dir: str = "data/output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _make_path(self, company: str, fiscal_year: int, label: str) -> str:
        filename = f"{company}_{fiscal_year}_{label}.csv"
        return os.path.join(self.output_dir, filename)

    def export_snippets(self, snippets: List[str], meta: FilingMeta) -> str:
        """Export raw restructuring text snippets from get_restructure()."""
        filepath = self._make_path(meta.company, meta.fiscal_year, "snippets")

        with open(filepath, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=["company", "cik", "fiscal_year", "snippet"])
            writer.writeheader()
            for snippet in snippets or []:
                writer.writerow({
                    "company": meta.company,
                    "cik": meta.cik,
                    "fiscal_year": meta.fiscal_year,
                    "snippet": snippet,
                })

        print(f"Exported snippets to {filepath}")
        return filepath

    def export_llm_results(self, llm_answers: dict, meta: FilingMeta) -> str:
        """Export the LLM's answers to the final CSV dataset."""
        filepath = self._make_path(meta.company, meta.fiscal_year, "llm_results")

        fieldnames = ["company", "cik", "fiscal_year"] + list(llm_answers.keys())

        with open(filepath, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                "company": meta.company,
                "cik": meta.cik,
                "fiscal_year": meta.fiscal_year,
                **llm_answers,
            })

        print(f"Exported LLM results to {filepath}")
        return filepath

    def export_full_dataset(self, records: List[dict], output_filename: str = "final_dataset.csv") -> str:
        """Combine all companies' LLM results into one final CSV dataset."""
        filepath = os.path.join(self.output_dir, output_filename)

        if not records:
            print("No records to export.")
            return filepath

        fieldnames = list(dict.fromkeys(k for r in records for k in r.keys()))

        with open(filepath, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

        print(f"Exported full dataset to {filepath}")
        return filepath