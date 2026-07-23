"""
Unified wrapper for LLM calls.

Constraint:
Instead of relying on function calling / tool use, the prompt explicitly
requires the model to return strict JSON, which is then parsed manually
via parse_json_response(). This approach avoids depending on whether a
specific model or gateway supports function calling, as long as it exposes
an OpenAI-compatible API.
"""

import json
import re
from typing import Dict, Any

from openai import AsyncOpenAI

from taxonomy_classification.src.config.llm_setting import (
    BULK_WORKER_MODEL_KEY,
    BULK_WORKER_MODEL_URL,
    BULK_WORKER_EXTRA_HEADERS,
    BULK_WORKER_MODEL,
    BULK_WORKER_EXTRA_BODY
)

client = AsyncOpenAI(
    api_key=BULK_WORKER_MODEL_KEY,
    base_url=BULK_WORKER_MODEL_URL,
    default_headers=BULK_WORKER_EXTRA_HEADERS,
)


async def chat(prompt: str) -> str:
    """
    Sends a prompt to the LLM (OpenAI-compatible API) and returns the
    generated text. Returns an empty string if no content is produced.
    """
    kwargs = {
        "model": BULK_WORKER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }

    if BULK_WORKER_EXTRA_BODY:
        kwargs["extra_body"] = BULK_WORKER_EXTRA_BODY

    response = await client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""


def parse_json_response(text: str) -> Dict[str, Any]:
    """
    Parses a JSON object from the LLM response.

    The model may wrap the JSON inside a Markdown code block such as
    ```json ... ```. If present, the wrapper is removed before calling
    json.loads().
    """
    cleaned = text.strip()

    match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1).strip()

    return json.loads(cleaned)


async def chat_json(prompt: str) -> Dict[str, Any]:
    """
    Calls the LLM and directly returns the parsed JSON object for modules
    requiring structured outputs.
    """
    raw_text = await chat(prompt)
    return parse_json_response(raw_text)