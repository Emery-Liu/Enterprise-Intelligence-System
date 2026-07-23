from openai import OpenAI

from entity_extraction.src.config.llm_setting import (
    BULK_WORKER_MODEL,
    BULK_WORKER_MODEL_URL,
    BULK_WORKER_MODEL_KEY,
    BULK_WORKER_EXTRA_BODY,
    BULK_WORKER_EXTRA_HEADERS
)

client = OpenAI(
    api_key=BULK_WORKER_MODEL_KEY,
    base_url=BULK_WORKER_MODEL_URL,
    default_headers=BULK_WORKER_EXTRA_HEADERS
)


def chat(prompt: str) -> str:
    """
    Send prompts to the company's internal LLM (OpenAI compatible protocol) to 
    eturn the model-generated text content; If there is no content, returns an empty string
    """
    kwargs = {
        "model": BULK_WORKER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }

    # Only pass additional parameters if they are configured to avoid passing unnecessary 
    # parameters to vendors that do not support these fields
    if BULK_WORKER_EXTRA_BODY:
        kwargs["extra_body"] = BULK_WORKER_EXTRA_BODY

    response = client.chat.completions.create(**kwargs)

    return response.choices[0].message.content or ""