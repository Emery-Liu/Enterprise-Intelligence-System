"""
Functionality:
1. Retrieve all leaf paths in the taxonomy
2. Convert leaf paths to text
3. Generate vectors using an embedding model
4. Build a FAISS index
5. Retrieve candidate industry paths based on a company’s business profile


Note:
The taxonomy itself does not have descriptions,
so the embedding text uses the full path:

Example：

Path in Chinese:
生物医药 > 生物+ > 合成生物 > 应用层 > 化工能源


"""
from typing import List
import json
import os
import faiss
import numpy as np


class TaxonomyIndex:

    def __init__(
        self,
        tree,
        embedding_model
    ):
        self.tree = tree
        self.embedding_model = embedding_model
        self.index = None
        self.leaf_paths: List[List[str]] = []

    # ------------------------------------------------------------------
    # Index build offline
    # ------------------------------------------------------------------

    def build(self):
        """
        Build Faiss Index
        """
        self.leaf_paths = self.tree.get_all_leaves() # List[List[str]]
        texts = [
            self._path_to_text(path)
            for path in self.leaf_paths
        ]
        '''
        Input example:
        [
            ["制造业", "汽车制造", "新能源汽车"],
            ["制造业", "机械制造"]
        ]
        Output example: 
        [
           "制造业 > 汽车制造 > 新能源汽车",     
           "制造业 > 机械制造"
        ] list of str
        '''
        vectors = self.embedding_model.embed_batch(texts) #looking embedding_client.py  List[List[Float]]
        vectors = np.array(vectors, dtype="float32") # convert numpy

        # cosine similarity
        # normalize in advance

        faiss.normalize_L2(vectors) # current embedding service already normalize vectors
        dim = vectors.shape[1] # dimesion check, 1024 dim here
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(vectors)


    # ------------------------------------------------------------------
    # candidate search
    # ------------------------------------------------------------------

    def search_candidate_branches(
        self,
        query: str,
        top_k: int = 20
    ) -> List[dict]:

        if self.index is None:
            raise RuntimeError(
                "Taxonomy index has not been built."
            )
        query_vector = self.embedding_model.embed(query)
        query_vector = np.array([query_vector], dtype="float32")
        faiss.normalize_L2(query_vector)

        scores, indices = self.index.search(
            query_vector,
            top_k
        )
        results = []

        for score, idx in zip(
            scores[0],
            indices[0]
        ):

            if idx == -1:
                continue

            results.append(
                {
                    "path": self.leaf_paths[idx],
                    "score": float(score)
                }
            )

        return results

    def _path_to_text(self, path: List[str]) -> str:
        return " > ".join(path)

    # ------------------------------------------------------------------
    # save & load
    # ------------------------------------------------------------------

    def save(self, index_dir: str):

        os.makedirs(index_dir, exist_ok=True)
        
        index_path = os.path.join(index_dir, "leaf_index.faiss")
        paths_path = os.path.join(index_dir, "leaf_paths.json")

        faiss.write_index(self.index, index_path)

        with open(paths_path, "w", encoding="utf-8") as f:
            json.dump(
                self.leaf_paths,
                f,
                ensure_ascii=False,
                indent=2
                )



    def load(self, index_dir: str):
        index_path = os.path.join(index_dir, "leaf_index.faiss")
        paths_path = os.path.join(index_dir, "leaf_paths.json")
        self.index = faiss.read_index(index_path)
        with open(
            paths_path,
            "r",
            encoding="utf-8"
            ) as f:
            self.leaf_paths = json.load(f)