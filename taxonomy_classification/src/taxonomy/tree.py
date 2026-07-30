"""
The raw data file for the tree: config/taxonomy.json
The path is specified by TAXONOMY_PATH in config/settings.py and is not hard-coded in this file.

Conventions:
1. A node is the key of a dict; a node's child nodes are the corresponding values (also a dict).
2. An empty dict {} represents a leaf node.
3. Nodes with the same name but different paths are not considered—that is, node names are globally unique across the entire tree,
   so a global index can be created directly using the node name: name -> full_path.
"""

import json
from typing import Dict, List


class IndustryTree:
    def __init__(self, taxonomy_path: str):
        self.taxonomy_path = taxonomy_path
        self.tree: Dict = self._load(taxonomy_path)
        self.path_index: Dict[tuple[str, ...], Dict] = {}
        self._build_index(self.tree, [])                           

    # -------------------------------------------------------------------
    # load & index build
    # -------------------------------------------------------------------
    def _load(self, path: str) -> Dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) # convert to dict

    def _build_index(self, node: Dict, current_path: List[str]) -> None:
        if not isinstance(node, dict):
            raise TypeError(
                f"Taxonomy node must be a dict, got {type(node).__name__}"
            )

        for name, children in node.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError(
                    f"Taxonomy node name must be a non-empty string, got {name!r}"
                )

            if not isinstance(children, dict):
                raise TypeError(
                    f"Children of taxonomy node {name!r} must be a dict, "
                    f"got {type(children).__name__}"
                )

            path = current_path + [name]
            path_key = tuple(path)

            if path_key in self.path_index:
                raise ValueError(
                    f"Duplicate taxonomy path detected: {' > '.join(path)}"
                )

            self.path_index[path_key] = children

            self._build_index(children, path)
    

    # -------------------------------------------------------------------
    # for external use
    # -------------------------------------------------------------------

    def get_children(self, path: List[str]) -> List[str]:
        """
        Return the direct child names of a valid taxonomy node.

        An empty list means the path is a valid leaf node.
        An invalid path raises ValueError instead of being treated as a leaf.
        """
        path_key = tuple(path)

        if path_key not in self.path_index:
            raise ValueError(
                f"Invalid taxonomy path: {' > '.join(path)}"
            )

        node = self.path_index[path_key]
        return list(node.keys())

    def is_valid_path(self, path: List[str]) -> bool:
        """Determine whether a non-empty path can be fully matched in the tree."""
        if not path:
            return False

        return tuple(path) in self.path_index 

    def is_leaf(self, path: List[str]) -> bool:
        """
        Determine whether a valid taxonomy node is a leaf node.
        """
        if not self.is_valid_path(path):
            raise ValueError(
                f"Cannot determine leaf status for invalid path: "
                f"{' > '.join(path)}"
            )

        return len(self.path_index[tuple(path)]) == 0

    def get_all_leaves(self) -> List[List[str]]:
        """DFS collects the complete paths of all leaf nodes for use by `tree_index.py` in building the embedding index."""
        leaves = []

        def dfs(node: Dict, current_path: List[str]):
            for name, children in node.items():
                path = current_path + [name]
                if isinstance(children, dict) and children:
                    dfs(children, path)
                else:
                    leaves.append(path)

        dfs(self.tree, [])
        return leaves