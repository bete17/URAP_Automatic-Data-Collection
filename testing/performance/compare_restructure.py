import re
from collections import Counter
from typing import Dict, List
import os


def normalize_text(text: str) -> str:
    """Lowercase and normalize whitespace/punctuation for robust comparisons."""
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> List[str]:
    """Tokenize normalized text into words."""
    normalized = normalize_text(text)
    return normalized.split() if normalized else []


def word_overlap_counts(auto_text: str, manual_text: str) -> Dict[str, int]:
    """
    Bag-of-words overlap counts.
    TP: overlap count; FP: auto-only count; FN: manual-only count.
    """
    auto_counter = Counter(tokenize(auto_text))
    manual_counter = Counter(tokenize(manual_text))

    tp = sum((auto_counter & manual_counter).values())
    fp = sum((auto_counter - manual_counter).values())
    fn = sum((manual_counter - auto_counter).values())
    return {"tp": tp, "fp": fp, "fn": fn}


def precision_score(auto_text: str, manual_text: str) -> float:
    """Precision = TP / (TP + FP)."""
    counts = word_overlap_counts(auto_text, manual_text)
    denom = counts["tp"] + counts["fp"]
    return counts["tp"] / denom if denom else 0.0


def recall_score(auto_text: str, manual_text: str) -> float:
    """Recall = TP / (TP + FN)."""
    counts = word_overlap_counts(auto_text, manual_text)
    denom = counts["tp"] + counts["fn"]
    return counts["tp"] / denom if denom else 0.0


def f1_score(auto_text: str, manual_text: str) -> float:
    """F1 = harmonic mean of precision and recall."""
    precision = precision_score(auto_text, manual_text)
    recall = recall_score(auto_text, manual_text)
    denom = precision + recall
    return 2 * precision * recall / denom if denom else 0.0


def jaccard_similarity(auto_text: str, manual_text: str) -> float:
    """Set-level Jaccard similarity on normalized word tokens."""
    auto_set = set(tokenize(auto_text))
    manual_set = set(tokenize(manual_text))
    union = auto_set | manual_set
    return (len(auto_set & manual_set) / len(union)) if union else 1.0


def shared_word_percentage(auto_text: str, manual_text: str) -> float:
    """
    Percentage of manual words covered by auto output.
    Equivalent to recall * 100.
    """
    return recall_score(auto_text, manual_text) * 100.0


def length_ratio(auto_text: str, manual_text: str) -> float:
    """Token length ratio auto/manual; returns 0.0 if manual is empty."""
    auto_len = len(tokenize(auto_text))
    manual_len = len(tokenize(manual_text))
    return (auto_len / manual_len) if manual_len else 0.0


def evaluate_pair(auto_text: str, manual_text: str) -> Dict[str, float]:
    """Return a metric bundle for one automatic-vs-manual pair."""
    return {
        "precision": precision_score(auto_text, manual_text),
        "recall": recall_score(auto_text, manual_text),
        "f1": f1_score(auto_text, manual_text),
        "jaccard": jaccard_similarity(auto_text, manual_text),
        "shared_word_pct": shared_word_percentage(auto_text, manual_text),
        "length_ratio": length_ratio(auto_text, manual_text),
    }

def get_auto_restructure(filepath, fyear, gvkey) -> List[str]:
    return None

def get_manual_restructure(filepath, fyear, gvkey) -> List[str]:
    return None

def main() -> None:

   auto_restructure = get_auto_restructure(filepath_auto, fyear1, gvkey1)
   manual_restructure = get_manual_restructure(filepath_manual, fyear2, gvkey2)
   metrics = evaluate_pair(auto_restructure, manual_restructure)
   print(metrics)


if __name__ == "__main__":
    main()
