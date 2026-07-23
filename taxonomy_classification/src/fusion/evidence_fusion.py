"""
Multi-source evidence fusion.

Responsibilities:
Processes the multiple evidence sources contained in CompanyInput
(baike/patent/project/web/yuqing) by cleaning, deduplicating, and
summarizing long documents when necessary, then assembles them into a
single unified evidence context ordered by source reliability.

The resulting context is consumed by:
- candidate_generator.py (enterprise profiling)
- hierarchical_reasoner.py (hierarchical taxonomy reasoning)

Evidence priority (highest → lowest reliability):
baike_data > patent_data_list > project_data_list > web_data_list > yuqing_data_list
"""

from typing import List, Tuple

from taxonomy_classification.src.api.classification_models import CompanyInput, SourceItem
from taxonomy_classification.src.preprocess.classification_cleaner import clean_text
from taxonomy_classification.src.preprocess.dedup import dedup_texts
from taxonomy_classification.src.preprocess.summarizer import summarize_if_needed


async def _prepare_list(
    source_type: str,
    items: List[SourceItem],
    company: str,
) -> List[str]:
    """
    Processes one list-based evidence source (e.g., patent_data_list):
    filter valid entries → clean → deduplicate → summarize.
    """

    valid_items = [item for item in items if item.is_valid]
    print(
        f"[evidence_fusion] {source_type}: "
        f"{len(items)} original, {len(valid_items)} valid"
    )


    if not valid_items:
        return []

    cleaned_texts = [clean_text(item.content) for item in valid_items]

    deduped_texts = dedup_texts(cleaned_texts)
    print(
        f"[evidence_fusion] {source_type}: "
        f"{len(cleaned_texts)} after cleaning, "
        f"{len(deduped_texts)} after deduplication "
        f"({len(cleaned_texts) - len(deduped_texts)} duplicates removed)"
    )


    summarized_texts = []
    for idx, text in enumerate(deduped_texts):
        original_len = len(text)
        summary = await summarize_if_needed(
            company=company,
            source_type=source_type,
            text=text,
        )
        if original_len > len(summary):
            print(
                f"[evidence_fusion] {source_type} item {idx + 1}: "
                f"summarization triggered "
                f"({original_len} chars → {len(summary)} chars)"
            )
        summarized_texts.append(summary)

    return summarized_texts


async def fuse_evidence(data: CompanyInput) -> str:
    """
    Entry point.

    Fuses all available evidence for an enterprise into a single
    context string.
    """

    company = data.company
    print(f"[evidence_fusion] ===== Processing enterprise: {company} =====")

    sections: List[Tuple[str, List[str]]] = []

     # Process baike_data separately (single record instead of a list).
    if data.baike_data and data.baike_data.is_valid:
        cleaned = clean_text(data.baike_data.content)
        summarized = await summarize_if_needed(
            company=company,
            source_type="baike_data",
            text=cleaned,
        )
        sections.append(("baike_data", [summarized]))
        print(
            f"[evidence_fusion] baike_data: "
            f"valid ({len(summarized)} characters)"
        )
    else:
        print("[evidence_fusion] baike_data: no valid content, skipped")

     # Process the remaining list-based evidence in descending reliability.
    list_fields = [
        ("patent_data_list", data.patent_data_list),
        ("project_data_list", data.project_data_list),
        ("web_data_list", data.web_data_list),
        ("yuqing_data_list", data.yuqing_data_list),
    ]

    for source_type, items in list_fields:
        texts = await _prepare_list(source_type, items, company)
        sections.append((source_type, texts))

    # Assemble the final context while preserving evidence priority.
    # Each source is grouped under its own label.
    context_parts = []
    for source_type, texts in sections:
        if not texts:
            continue
        block = "\n".join(f"- {t}" for t in texts)
        context_parts.append(f"【{source_type}】\n{block}")

    final_context = "\n\n".join(context_parts)

    print(
        f"[evidence_fusion] ===== Evidence fusion completed. "
        f"Final context length: {len(final_context)} characters ====="
    )

    return final_context