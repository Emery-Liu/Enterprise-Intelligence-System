from relevance_matching.src.api.relevance_models import (
    EnterpriseRelevanceRequest,
    EnterpriseRelevanceResponse,
)
from relevance_matching.src.core.relevance_pipeline import judge_enterprise_relevance


def check_enterprise_relevance(
    request: EnterpriseRelevanceRequest,
) -> EnterpriseRelevanceResponse:
    """
    企业-舆情关联判定业务入口。

    Args:
        request: 企业关联判定请求体

    Returns:
        EnterpriseRelevanceResponse
    """

    related = judge_enterprise_relevance(
        enterprise_name=request.enterprise_name,
        title=request.title,
        summary=request.summary,
        content=request.content,
    )

    return EnterpriseRelevanceResponse(
        related=related,
    )