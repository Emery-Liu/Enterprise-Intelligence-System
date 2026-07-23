"""
Candidate Branch Generation

Responsibilities:
1. Condense the company's fusion evidence text (output from `fusion/evidence_fusion.py`) into a
   concise “business profile” text (by calling an LLM).
2. Use this profile text to query the vector database (`taxonomy/tree_index.py`) and retrieve the
   Top-K most similar leaf nodes.
3. From the retrieved leaf node paths, extract the node names at the specified level (default: Level 1, i.e., one of the 9 top-level nodes),
   remove duplicates, and use them as candidate starting points for llm/hierarchical_reasoner.py
   to drill down layer by layer.
"""

from typing import List

from taxonomy_classification.src.config.llm_setting import CANDIDATE_TOP_K
from taxonomy_classification.src.llm.classification_client import chat
from taxonomy_classification.src.core.classification_prompts import build_summary_prompt
from taxonomy_classification.src.taxonomy.tree_index import TaxonomyIndex


async def build_company_profile(company: str, evidence_text: str) -> str:
    """Call the LLM to condense the merged evidence text into a concise business profile text for use in embedding retrieval."""
    prompt = build_summary_prompt(company=company, evidence_text=evidence_text)
    profile_text = (await chat(prompt)).strip()

    print(f"[candidate_generator] company profile: {profile_text}")

    return profile_text


async def get_candidate_branches(
    company: str,
    evidence_text: str,
    tree_index: TaxonomyIndex,
    top_k: int = None,
    branch_level: int = 1) -> List[dict]:
    """
    Generate a list of candidate starting branch names.

    branch_level: From the complete paths of the retrieved leaf nodes, specify which level of node names to use as candidate starting points.
                  The default is 1, which means using first-level node names (e.g., “Biopharmaceuticals”).
                  If you want more granular candidates (e.g., second-level nodes), you can pass branch_level=2.
    """
    top_k = top_k or CANDIDATE_TOP_K

    profile_text = await build_company_profile(company, evidence_text)

    results = tree_index.search_candidate_branches(profile_text, top_k)
    print(f"[candidate_generator] Vector retrieval returns {len(results)} leaf nodes")

    candidate_paths: List[dict] = []
    for r in results:
        path = r["path"]
        score = r["score"]
        print(f"[candidate_generator] path: {' > '.join(path)} (score={score:.3f})")

        if len(path) >= branch_level:
            candidate_path = path[:branch_level]
            if candidate_path not in [item["path"] for item in candidate_paths]:
                candidate_paths.append(
                    {
                        "path": candidate_path,
                        "score": score
                    }
                )

    print(f"[candidate_generator] Candidate startpoints (level {branch_level}, {len(candidate_paths)} in total): {candidate_paths}")

    return candidate_paths