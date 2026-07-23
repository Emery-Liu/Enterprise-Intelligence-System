"""
Path Deduplication/Merging.

Responsibilities:
Handle two types of redundancies that may appear in the final list of industrial paths:

1. Completely duplicate paths
   (For example, two different candidate starting branches ultimately drill down to the same path).

2. Paths with an “ancestor-descendant” relationship
    Retain the deepest path that the LLM can analyze
"""

from typing import List

def merge_paths(paths: List[dict]) -> List[dict]:
    """
    Remove duplicate path and Retain the deepest path that the LLM can analyze。
    """
    print(f"[dedup_merge] path counts: {len(paths)}")

    # Step 1
    unique_items = []
    seen_paths = set()
    for item in paths:
        path_tuple = tuple(item["path"])
        if path_tuple not in seen_paths:
            seen_paths.add(path_tuple)
            unique_items.append(item)

    # Step 2
    final_paths = []
    for i, item_a in enumerate(unique_items):
        path_a = item_a["path"]
        
        is_subsumed = False
        for j, item_b in enumerate(unique_items):
            if i == j:
                continue
            path_b = item_b["path"]
            
            if len(path_b) > len(path_a) and path_b[:len(path_a)] == path_a:
                is_subsumed = True
                print(f"[dedup_merge]   remove shorter path: {path_a} is overlaped by {path_b})")
                break
        
        if not is_subsumed:
            final_paths.append(item_a)

    print(f"[dedup_merge] final paths: {len(final_paths)} paths")
    return final_paths