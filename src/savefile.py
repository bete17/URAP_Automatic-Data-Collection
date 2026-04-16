import os
import csv
from typing import Any, Iterable, Optional

class FileExporter:
    def __init__(self, output_dir, cik, year):
        self.output_dir = output_dir
        self.cik = cik
        self.year = year

    def get_gvkey(self):
        """Get the gvkey for the given cik and year from sample_all.csv

        Returns:
            str: The gvkey corresponding to the given cik and year
        """
        sample_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "data", "sample_all.csv")
        )

        cik = str(self.cik).strip()
        # `sample_all.csv` stores CIK as a 10-digit, zero-padded string.
        if cik.isdigit():
            cik = cik.zfill(10)

        try:
            year = int(self.year)
        except (TypeError, ValueError):
            year = None

        with open(sample_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_cik = (row.get("cik") or "").strip()
                if row_cik.isdigit():
                    row_cik = row_cik.zfill(10)

                if row_cik != cik:
                    continue

                if year is not None:
                    try:
                        row_year = int((row.get("fyear") or "").strip())
                    except ValueError:
                        continue
                    if row_year != year:
                        continue

                gvkey = (row.get("gvkey") or "").strip()
                return gvkey or None

        return None
    
    def save_restructuring(self, item7_hits, item8_hits):
        """Save the restructuring-blocks in files in [txt] format for item 7 and item 8 respectively

        Args:
            hits (List[Block]): Restructuring-related blocks
            filepath7 (str): Path to the output file for item 7
            filepath8 (str): Path to the output file for item 8

        Returns:
            None
        """

        os.makedirs(self.output_dir, exist_ok=True)

        gvkey = str(self.get_gvkey())
        stem_parts = [p for p in [gvkey, str(self.year).strip()] if p]
        stem = "_".join(stem_parts) if stem_parts else "export"

        path7 = os.path.join(self.output_dir, f"{stem}_item7.txt")
        path8 = os.path.join(self.output_dir, f"{stem}_item8.txt")

        self._write_hits(path7, item7_hits, section_label="ITEM 7")
        self._write_hits(path8, item8_hits, section_label="ITEM 8")
        return None

    def _write_hits(self, filepath: str, hits: Optional[Iterable[Any]], section_label: str) -> None:
        """
        Handles file writing for either section
        """
        payload = self._hits_to_text(hits)
        with open(filepath, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"{section_label}\n")
            f.write(payload)
            if payload and not payload.endswith("\n"):
                f.write("\n")

    def _hits_to_text(self, hits: Optional[Iterable[Any]]) -> str:
        """
        builds the final text for the section
        """
        chunks = []
        for hit in hits or []:
            idx, block = self._unpack_hit(hit)
            text = self._block_to_text(block)
            if not text:
                continue
            header = f"--- hit index: {idx} ---\n" if idx is not None else "--- hit ---\n"
            chunks.append(header + text.rstrip() + "\n")
        return "\n".join(chunks).rstrip() + ("\n" if chunks else "")

    def _unpack_hit(self, hit: Any) -> tuple[Optional[int], Any]:
        # Supports either Block objects directly, or the dict records produced by
        # Extract_Restructure.capture_hits: {"index": int, "block": Block}
        if isinstance(hit, dict):
            idx = hit.get("index")
            try:
                idx = int(idx) if idx is not None else None
            except (TypeError, ValueError):
                idx = None
            return idx, hit.get("block")
        return None, hit

    def _block_to_text(self, block: Any) -> str:
        """
        Converts a block to text
        """
        if block is None:
            return ""

        btype = getattr(block, "type", None)
        if btype == "paragraph":
            return (getattr(block, "text", "") or "").strip()

        if btype == "table":
            rows = getattr(block, "rows", None) or []
            return "\n".join("\t".join((cell or "").strip() for cell in row) for row in rows).strip()

        if isinstance(block, str):
            return block.strip()

        # Fallback for unexpected shapes
        return str(block).strip()
    