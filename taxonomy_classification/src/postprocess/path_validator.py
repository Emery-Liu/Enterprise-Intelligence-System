"""
Path Validity Check (The Final Line of Defense in Post-processing).

Responsibilities:
Although llm/hierarchical_reasoner.py has already performed a check during the drill-down process to ensure that "child nodes must be within
the scope of tree.get_children()," this step performs an independent, comprehensive path-level
hard validation—without relying on the LLM or upstream modules—by directly using `is_valid_path()` from `taxonomy/tree.py`
to verify each level, ensuring that the final output contains no paths that do not exist in the tree.
.
"""

from typing import List

from taxonomy_classification.src.taxonomy.tree import IndustryTree


def validate_path(path: List[str], tree: IndustryTree) -> bool:
    """Determine whether a path can be fully matched on the tree。"""
    return tree.is_valid_path(path)


def fallback_to_ancestor(path: List[str], tree: IndustryTree) -> List[str]:
    """
    When a path is invalid, truncate it layer by layer starting from the end to find the
    deepest valid ancestor path that matches in the tree. If even the root node is invalid, return an empty list.
    """
    for i in range(len(path), 0, -1):
        candidate = path[:i]
        if tree.is_valid_path(candidate):
            return candidate
    return []


def validate_paths(paths_data: List[dict], tree: IndustryTree) -> List[dict]:
    """
    receving List[dict], format {'path': [...], 'reasoning_chain': [...]}
    """
    validated_results: List[dict] = []

    for item in paths_data:
        path = item['path']
        print(f"[path_validator] check: {path}")

        if validate_path(path, tree):
            validated_results.append(item)
            continue

        fallback = fallback_to_ancestor(path, tree)
        if fallback:
            print(f"[path_validator] illegal, fallback to: {fallback}")
            new_item = {
                "path": fallback,
                "reasoning_chain": item['reasoning_chain'][:len(fallback)],
                "score": item["score"]
            }
            validated_results.append(new_item)
        else:
            print("[path_validator] illegal, and cannot fallback")

    return validated_results