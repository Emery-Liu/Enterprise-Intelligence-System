import logging
import time
import uuid

from dotenv import load_dotenv
load_dotenv()

from taxonomy_classification.src.logging_config import setup_logging 
setup_logging()
logger = logging.getLogger("Company Classification")

import uvicorn
from fastapi import FastAPI, HTTPException

#=================== Classification import===========================
from taxonomy_classification.src.api.classification_models import (
    CompanyInput,
    ClassificationResult,
    PathResult
)
from taxonomy_classification.src.core.classification_pipeline import classify_company
from taxonomy_classification.src.taxonomy.tree import IndustryTree
from taxonomy_classification.src.taxonomy.tree_index import TaxonomyIndex
from taxonomy_classification.src.config.llm_setting import TAXONOMY_PATH, EMBEDDING_INDEX_DIR
from taxonomy_classification.src.embedding.embedding_client import EmbeddingClient

#=================== FASTAPI Title ===========================
app = FastAPI(title="Company Classification")

#=================== Classification Service ==========================
tree = IndustryTree(TAXONOMY_PATH)
embedding_model = EmbeddingClient()
tree_index = TaxonomyIndex(
    tree=tree,
    embedding_model=embedding_model
)

tree_index.load(EMBEDDING_INDEX_DIR)

@app.post("/company_field_classify", response_model=ClassificationResult)
async def classify_company_api(data: CompanyInput):
    """
    Company industry classification
    """
    request_id = str(uuid.uuid4())[:8]
    start_time = time.perf_counter()

    
    try:
        result_dicts = await classify_company(
            data=data,
            tree=tree,
            tree_index=tree_index,
        )

        path_results = []

        for item in result_dicts:
            if isinstance(item, dict):
                path_results.append(PathResult(**item))
            else:
                path_results.append(PathResult(
                    path=item.path, 
                    reasoning_chain=item.reasoning_chain,
                    score=round(item.score, 2)
                ))
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )
        logger.info(
            "Request Success",
            extra={
                "request_id": request_id,
                "endpoint": "/company_field_classify",
                "duration_ms": duration_ms,
                "status": "success",
                "result_count": len(path_results),
            },
        )
        
        return {"paths": path_results}

    except Exception as exc:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.error(
            "Request Fail",
            extra={
                "request_id": request_id,
                "endpoint": "/company_field_classify",
                "duration_ms": duration_ms,
                "status": "error",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
            exc_info=True,
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Company Field Classification Service Error [{request_id}]",
)


if __name__ == '__main__':
    port = 10
    uvicorn.run(app=app,
                host="0.0.0.0",
                port=port,
                reload=False,
                workers=1)
