"""
Responsibilities:
Starting from the root of a candidate branch, recursively traverse the taxonomy
tree by invoking the LLM level by level. At each level, the model is presented
only with the direct children of the current node and is allowed to make
multiple selections. This guarantees that the LLM can never generate a category
that does not exist in the taxonomy (the selected paths are also validated
afterward).

Termination Rules (Important):
1. If the current node is already a leaf node (i.e., it has no children),
   it is directly returned as a final classification path without further
   LLM calls.

2. If the current node is not a leaf but the LLM determines that none of
   its child categories are clearly applicable (selected_children is empty),
   the traversal stops at the current node, which is returned as the final
   classification path. The algorithm does not force traversal to a leaf.

3. A single candidate branch may produce multiple final paths because the
   LLM is allowed to select multiple child categories at each level. Each
   selected child is explored independently until it reaches its deepest
   applicable node.
"""

from typing import List

from taxonomy_classification.src.taxonomy.tree import IndustryTree
from taxonomy_classification.src.llm.classification_client import chat_json
from taxonomy_classification.src.core.classification_prompts import build_layer_selection_prompt
from taxonomy_classification.src.api.classification_models import LayerSelection


async def reason_layer(
    company: str,
    parent_path: List[str],
    evidence_text: str,
    tree: IndustryTree,
) -> LayerSelection:
    """
    Given a parent_path (the full path of the current taxonomy node),
    invokes the LLM to select the applicable categories from its direct
    child nodes.
    """
    children = tree.get_children(parent_path)

    print(f"[hierarchical_reasoner] reason_layer: parent_path={parent_path}, candidate node={children}")

    prompt = build_layer_selection_prompt(
        company=company,
        parent_path=parent_path,
        children=children,
        evidence_text=evidence_text,
    )

    try:
        raw_result = await chat_json(prompt)
        selection = LayerSelection(**raw_result)

    except Exception as e:
        print(
        f"[hierarchical_reasoner] LLM return parse fail: {e}，"
        f"current node {parent_path} stop drill down"
    )

        selection = LayerSelection(
            parent_path=parent_path,
            selected_children=[],
            reasoning=f"LLM parse fail: {str(e)}")
    print(f"[hierarchical_reasoner] LLM choose: "
            f"{selection.selected_children}, "
            f"reason: {selection.reasoning}")

    return selection


async def traverse_branch(
    company: str,
    start_path: List[str],
    evidence_text: str,
    tree: IndustryTree,
    score: float
) -> List[dict]:
    final_paths: List[dict] = []
    '''
    Note: there is no first level reasoning present
    '''
    initial_chain = []

    async def _dfs(current_path: List[str], current_reasoning_chain: List[str], score: float) -> None:
        children = tree.get_children(current_path)
        
        # stop at leaf
        if not children:
            final_paths.append({"path": current_path, 
                                "reasoning_chain": current_reasoning_chain,
                                "score": score})
            return

        # selection is for next level
        selection = await reason_layer(company, current_path, evidence_text, tree)

        # terminate：LLM has no candidate next level node
        if not selection.selected_children:
            print(
                f"[hierarchical_reasoner] No subcategories have been selected for the current node {current_path}; drilling down has stopped."
            )

            final_paths.append({
                "path": current_path,
                "reasoning_chain": current_reasoning_chain,
                "score": score
            })

            return
            
        for child in selection.selected_children:
            if child not in children:
                continue
            
            # Store the reason for the drill-down in the reasoning chain
            new_chain = current_reasoning_chain + [selection.reasoning or "No detailed reasoning provided"]
            await _dfs(current_path + [child], new_chain, score)

    # 3. initiate dfs
    await _dfs(start_path, initial_chain, score)
    
    return final_paths


async def reason_all_branches(
    company: str,
    candidate_root_paths: List[dict],
    evidence_text: str,
    tree: IndustryTree,
) -> List[dict]:
    """
    Performs hierarchical reasoning for each candidate root branch
    retrieved by retrieval/candidate_generator.py, then aggregates
    all final classification paths.
    """
    print(f"[hierarchical_reasoner] ===== Start Reasoning: Candidate Start: {candidate_root_paths} =====")

    all_paths: List[List[str]] = []
    for root_name in candidate_root_paths:
        paths = await traverse_branch(company, root_name["path"], evidence_text, tree, root_name["score"])
        all_paths.extend(paths)
    filtered_paths = [
    path
    for path in all_paths
    if len(path["path"]) > 1
    ]
    print(f"[hierarchical_reasoner] ===== reasoning stop, provide{len(filtered_paths)} paths =====")

    return filtered_paths