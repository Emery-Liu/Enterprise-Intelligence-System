from taxonomy_classification.src.api.classification_models import CompanyInput, ClassificationResult

from taxonomy_classification.src.fusion.evidence_fusion import fuse_evidence

from taxonomy_classification.src.retrieval.candidate_generator import get_candidate_branches

from taxonomy_classification.src.llm.hierarchical_reasoner import reason_all_branches

from taxonomy_classification.src.taxonomy.tree import IndustryTree
from taxonomy_classification.src.taxonomy.tree_index import TaxonomyIndex

from taxonomy_classification.src.postprocess.path_validator import validate_paths
from taxonomy_classification.src.postprocess.dedup_merge import merge_paths
from taxonomy_classification.src.api.classification_models import PathResult

CONFIDENCE_SCALE = 1.65
MAX_CONFIDENCE = 0.99

async def classify_company(
    data: CompanyInput,
    tree: IndustryTree,
    tree_index: TaxonomyIndex,
) -> ClassificationResult:
    """
    Main pipeline for enterprise taxonomy classification.
    """
    evidence_text = await fuse_evidence(data)

    candidate_root_paths = await get_candidate_branches(
        company=data.company,
        evidence_text=evidence_text,
        tree_index=tree_index,
        branch_level=1
    )

    paths = await reason_all_branches(
        company=data.company,
        candidate_root_paths=candidate_root_paths,
        evidence_text=evidence_text,
        tree=tree,
    )

    paths = validate_paths(paths, tree)

    paths = merge_paths(paths)

    return [
        PathResult(
            path=p["path"],
            reasoning_chain=p["reasoning_chain"],
            score=min(p["score"] * CONFIDENCE_SCALE, MAX_CONFIDENCE)
        )
        for p in paths
    ]


'''
The original vector similarity scores tend to be systematically low because
enterprise profiles are represented as relatively long texts containing
multi-domain information and inevitable semantic noise.

A linear calibration is therefore applied to improve the confidence scores
presented to downstream business applications. This adjustment preserves the
relative ranking between candidates and does not affect the classification
logic itself; it only improves the interpretability of the displayed
confidence values.
'''