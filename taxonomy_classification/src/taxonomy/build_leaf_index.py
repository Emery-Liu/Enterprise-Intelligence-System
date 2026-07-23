'''
Offline script: Convert the path text of all leaf nodes in the industrial tree into embedding, constructing the FAISS vector index.

This is an offline task that "only needs run once":
- Input: config/taxonomy.json (loaded via IndustryTree)
- Output: Two files, written to settings. EMBEDDING_INDEX_DIR Specified directory
    1. leaf_index.faiss — FAISS IndexFlatIP vector index
    2. leaf_paths.json — A complete list of leaf nodes that correspond one-to-one to vectors in the index
'''

from dotenv import load_dotenv
load_dotenv()

from taxonomy_classification.src.config.llm_setting import TAXONOMY_PATH, EMBEDDING_INDEX_DIR
from taxonomy_classification.src.taxonomy.tree import IndustryTree
from taxonomy_classification.src.embedding.embedding_client import EmbeddingClient
from taxonomy_classification.src.taxonomy.tree_index import TaxonomyIndex


embedding_client = EmbeddingClient()
def build_leaf_index(output_dir: str = EMBEDDING_INDEX_DIR) -> None:
    tree = IndustryTree(TAXONOMY_PATH)
    taxonomy_index = TaxonomyIndex(tree=tree, embedding_model=embedding_client)
    taxonomy_index.build()
    taxonomy_index.save(output_dir)
'''
if __name__ == "__main__":
    build_leaf_index()
python3 -m main_chain_extract.taxonomy.build_leaf_index
'''