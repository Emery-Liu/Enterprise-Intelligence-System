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
        self.path_index: Dict[tuple[str, ...]] = {}
        self._build_index(self.tree, [])                           

    # -------------------------------------------------------------------
    # load & index build
    # -------------------------------------------------------------------
    def _load(self, path: str) -> Dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) # convert to dict

    def _build_index(self, node: Dict, current_path: List[str]) -> None:
        for name, children in node.items():
            self._build_index(children, current_path + [name])
    

    # -------------------------------------------------------------------
    # for external use
    # -------------------------------------------------------------------

    def get_children(self, path: List[str]) -> List[str]:
        """Returns a list of the names of a node's direct child nodes. An empty list indicates a leaf node"""
        node = self.path_index.get(tuple(path)) # tuple(path) is key，node as its return

        if node is None:
            return []
        return list(node.keys())

    def is_valid_path(self, path: List[str]) -> bool:
        """Determine whether a given path can be fully matched in the tree"""
        return tuple(path) in self.path_index 

    def is_leaf(self, path: List[str]) -> bool:
        """Determine whether a given node is leaf"""
        return len(self.get_children(path)) == 0

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