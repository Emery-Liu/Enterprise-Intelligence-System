import logging
import time
import uuid

from dotenv import load_dotenv
load_dotenv()

from entity_extraction.src.logging_config import setup_logging 
setup_logging()
logger = logging.getLogger("Company Entity Extraction")

import uvicorn
from fastapi import FastAPI, HTTPException

#=================== Extraction import===========================
from entity_extraction.src.api.models import ExtractCompaniesResponse, ExtractCompaniesRequest
from entity_extraction.src.api.service import extract_companies

#=================== FASTAPI Title ===========================
app = FastAPI(title="Company Extraction Service")

#=================== Extraction Service ==========================
@app.post("/extract_main_chain_companies", response_model=ExtractCompaniesResponse)
def extract_main_chain_companies(payload: ExtractCompaniesRequest) -> ExtractCompaniesResponse:
    """
    Retrieve business names that include the correct market entity type
    """
    request_id = str(uuid.uuid4())[:8]
    start_time = time.perf_counter()
    input_length = {
        "title": len(payload.title),
        "summary": len(payload.summary),
        "content": len(payload.content),
    }
    input_length["total"] = sum(input_length.values())
 
    try:
        if hasattr(payload, "model_dump"):
            payload_dict = payload.model_dump()
        else:
            payload_dict = payload.dict()
 
        companies = extract_companies(payload_dict)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
 
        logger.info(
            "Request Success",
            extra={
                "request_id": request_id,
                "endpoint": "/extract_main_chain_companies",
                "input_length": input_length,
                "duration_ms": duration_ms,
                "status": "success",
                "result_count": len(companies),
            },
        )
 
    except Exception as exc:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        companies = []
 
        logger.error(
            "Request Fail",
            extra={
                "request_id": request_id,
                "endpoint": "/extract_main_chain_companies",
                "input_length": input_length,
                "duration_ms": duration_ms,
                "status": "error",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Company Extraction Service Error [{request_id}]",
        )
 
    return ExtractCompaniesResponse(companies=companies)

if __name__ == '__main__':
    port = 100
    uvicorn.run(app=app,
                host="0.0.0.0",
                port=port,
                reload=False,
                workers=1)