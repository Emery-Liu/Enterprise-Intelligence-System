"""
Duplicate Removal for Multi-Source Text.

Scenario: In yuqing_data_list and web_data_list, it is common for the same news article to be reposted via multiple
links. The content is highly similar but not identical (e.g., clickbait-style rewrites or reposts with a few additional sentences added),
so using SimHash for approximate duplicate removal is more appropriate than exact string matching.
"""

from typing import List
from simhash import Simhash
import jieba


def compute_simhash(text: str) -> int:
    """
    Calculate the simhash after tokenizing(Chinese context)。
    """
    tokens = jieba.cut(text)
    return Simhash(tokens).value


def is_near_duplicate(hash_a: int, hash_b: int, threshold: int = 3) -> bool:
    """
    Determine whether two SimHash fingerprints constitute a near duplicate.

    threshold: The Hamming distance threshold; the smaller the value, the greater the required similarity. 
    The default value of 3 is a commonly used empirical threshold for SimHash
    """
    distance = bin(hash_a ^ hash_b).count("1")
    return distance <= threshold


def dedup_texts(texts: List[str], threshold: int = 3) -> List[str]:
    """
    Perform approximate deduplication on the list of text strings,
    retaining the first occurrence in each group of approximate duplicates.
    """
    kept_texts: List[str] = []
    kept_hashes: List[int] = []

    for text in texts:
        if not text:
            continue
        
        text_hash = compute_simhash(text)

        is_duplicate = any(
            is_near_duplicate(text_hash, kept_hash, threshold)
            for kept_hash in kept_hashes
        )

        if not is_duplicate:
            kept_texts.append(text)
            kept_hashes.append(text_hash)
    return kept_texts