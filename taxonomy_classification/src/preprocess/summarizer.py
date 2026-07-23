"""
Long-text summary.

Responsibilities:
Condense excessively long individual text segments to prevent lengthy documents—such as patents or project documents—
from being fed directly into subsequent LLM prompts, which would result in excessively long token counts.

"""

from taxonomy_classification.src.config.llm_setting import SUMMARIZE_TRIGGER_LENGTH
                                                   
from taxonomy_classification.src.llm.classification_client import chat
from taxonomy_classification.src.core.classification_prompts import build_document_summary_prompt


async def summarize_if_needed(
    company: str,
    source_type: str,
    text: str,
) -> str:
    """
    If the text length exceeds the threshold, the LLM summary is called;
    otherwise, the original text is returned directly
    """
    if not text:
        return ""

    if len(text) <= SUMMARIZE_TRIGGER_LENGTH:
        return text

    prompt = build_document_summary_prompt(
        company=company,
        source_type=source_type,
        text=text,
    )

    summary = await chat(prompt)
    return summary.strip()