import os
import json

BULK_WORKER_MODEL = os.environ.get("BULK_WORKER_MODEL")
BULK_WORKER_MODEL_URL = os.environ.get("BULK_WORKER_MODEL_URL")
BULK_WORKER_MODEL_KEY = os.environ.get("BULK_WORKER_MODEL_KEY")

BULK_WORKER_EXTRA_BODY = json.loads(
    os.environ.get("BULK_WORKER_EXTRA_BODY", '{}')
    )
BULK_WORKER_EXTRA_HEADERS = json.loads(
    os.environ.get("BULK_WORKER_EXTRA_HEADERS", '{}')
    )
