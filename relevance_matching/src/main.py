import logging
import time
import uuid

from dotenv import load_dotenv
load_dotenv()

from relevance_matching.src.logging_config import setup_logging 
setup_logging()
logger = logging.getLogger("Company Relevance Check")

import uvicorn
from fastapi import FastAPI, HTTPException
#=================== Relevance Matching import===========================
from relevance_matching.src.api.relevance_models import (
    EnterpriseRelevanceRequest,
    EnterpriseRelevanceResponse,
)
from relevance_matching.src.api.relevance_service import check_enterprise_relevance

#=================== Fast API title ===========================
app = FastAPI(title="Company Relevance Check")


#=================== Relevance Matching Service==========================
@app.post("/check_enterprise_relevance", response_model=EnterpriseRelevanceResponse)
def check_relevance(request: EnterpriseRelevanceRequest) -> EnterpriseRelevanceResponse:
    """
    Enterprise-Public Sentiment Correlation Analysis
    """
    request_id = str(uuid.uuid4())[:8]
    start_time = time.perf_counter()
    input_length = {
        "title": len(request.title) if request.title else 0,
        "summary": len(request.summary) if request.summary else 0,
        "content": len(request.content) if request.content else 0,
    }
    input_length["total"] = sum(input_length.values())


    try:
        response = check_enterprise_relevance(request)
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.info(
            "Request Success",
            extra={
                "request_id": request_id,
                "endpoint": "/check_enterprise_relevance",
                "input_length": input_length,
                "duration_ms": duration_ms,
                "status": "success",
            },
        )

        return response

    except Exception as exc:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.error(
            "Request Fail",
            extra={
                "request_id": request_id,
                "endpoint": "/check_enterprise_relevance",
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
            detail=f"Enterprise Relevance Service Error [{request_id}]",
)


if __name__ == '__main__':
    port = 1000
    uvicorn.run(app=app,
                host="0.0.0.0",
                port=port,
                reload=False,
                workers=1)