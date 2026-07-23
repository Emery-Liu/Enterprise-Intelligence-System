from typing import Any
from pydantic import BaseModel
from entity_extraction.src.api.models import ExtractCompaniesRequest
from entity_extraction.src.core.extraction_pipeline import CompanyExtractionPipeline


pipeline = CompanyExtractionPipeline()


def _normalize_payload(payload: dict[str, Any]) -> list[ExtractCompaniesRequest]:
    single_request = _parse_model(ExtractCompaniesRequest, payload)
    return [single_request]


def _parse_model(model_class: type[BaseModel], payload: dict[str, Any]) -> Any:
    '''
    Converts a dict into a Pydantic model object of the specified type, compatible with both v1 and v2 versions.
    '''
    if hasattr(model_class, "model_validate"):
        return model_class.model_validate(payload)
    return model_class.parse_obj(payload)


def _extract_unique_companies(requests: list[ExtractCompaniesRequest]) -> list[str]:
    seen: set[str] = set()
    companies: list[str] = []
    '''
    Traverse the request list, call pipeline.run() to extract company names, remove duplicates, 
    and then return a list of unique company names.
    '''
    for request in requests:
        extracted = pipeline.run(
            title=request.title,
            summary=request.summary,
            content=request.content,
        )
        for company in extracted:
            if company not in seen:
                seen.add(company)
                companies.append(company)
    return companies

def extract_companies(payload: dict[str, Any]) -> list[str]:
    '''
     The core of FastAPI route handlers consists of two steps—“parsing the request” 
     and “batch extraction and deduplication”—linked together.
    '''
    requests = _normalize_payload(payload)
    result = _extract_unique_companies(requests)
    return result