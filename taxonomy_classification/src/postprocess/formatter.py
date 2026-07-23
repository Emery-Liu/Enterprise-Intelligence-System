"""
Responsibilities:
Assemble the list of industry paths—which have been processed by `path_validator` 
(validity check) and `dedup_merge` (duplicate removal and merging) into the final standard output format 
for external use (corresponding to `schemas.io_schema.ClassificationResult`).

Example:
Paths are presented in Chinese
paths = [
    ["生物医药", "生物+", "合成生物", "应用层", "化工能源"],
    ["人工智能", "AI基础设施", "算力", "GPU", "国产GPU"],
]

Output：
{
    "paths": [
        ["生物医药", "生物+", "合成生物", "应用层", "化工能源"],
        ["人工智能", "AI基础设施", "算力", "GPU", "国产GPU"]
    ]
}
"""

from typing import List

from taxonomy_classification.src.api.classification_models import ClassificationResult
from taxonomy_classification.src.config.llm_setting import MAX_OUTPUT_PATHS

def format_output(paths: List[dict]) -> ClassificationResult:
    """
    Wrap the list of paths into a Pydantic object for standard output

    Pydantic v1:
        ClassificationResult.dict()
        ClassificationResult.json()
    """
    # Temporary measures to limit output volume in exchange for accuracy
    paths = paths[:MAX_OUTPUT_PATHS]
    
    return ({"path": p["path"], "reasoning_chain": p["reasoning_chain"]} 
            for p in paths)


def format_output_dict(paths: List[dict]) -> dict:
    """
    Returns a native dict.

    Used for:
    - API responses
    - Preprocessing before JSON serialization

    This project uses Pydantic v1, so dict() is used.。
    """

    return format_output(paths).dict()