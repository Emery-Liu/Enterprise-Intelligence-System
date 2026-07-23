from dotenv import load_dotenv
load_dotenv()

import requests

from taxonomy_classification.src.config.llm_setting import (
    EMBEDDING_URL,
    POD_NAME,
    POD_NAMESPACE,
)


class EmbeddingClient:
    """
    Wrapper around the embedding service.

    Responsibilities:
    1. Generate an embedding for a single text.
    2. Generate embeddings for a batch of texts.

    Returns:
    list[float] or list[list[float]]

    Note:
    The embedding service already returns L2-normalized vectors,
    so no additional normalization is required locally.
    """

    def __init__(self, timeout: int = 30):
        self.url = EMBEDDING_URL
        self.headers = {
            "podName": POD_NAME,
            "podNameSpace": POD_NAMESPACE,
            "Content-Type": "application/json",
        }

        self.timeout = timeout


    def embed(self, text: str) -> list[float]:
        response = requests.post(
            self.url,
            headers=self.headers,
            json={
                "data": [
                    {
                        "id": "0",
                        "text": text,
                    }
                ]
            },
            timeout=self.timeout,
        )

        response.raise_for_status()
        result = response.json()
        return result["data"][0]["vector"]


    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        data = [
            {
                "id": str(index),
                "text": text,
            }
            for index, text in enumerate(texts)  # IDs start from 0.
        ]
        '''
        data = [
            {
                "id": "0",
                "text": "Manufacturing > Automotive > New Energy Vehicles"
            },
            {
                "id": "1",
                "text": "Manufacturing > Machinery"
            }
        ]
        '''

        response = requests.post(
            self.url,
            headers=self.headers,
            json={
                "data": data,
            },
            timeout=self.timeout,
        )

        response.raise_for_status()  # Raise an exception if the HTTP request failed.

        result = response.json()  # Parse the JSON response into a Python dictionary.

        vectors = sorted(  # Restore the original order using the request IDs.
            result["data"],
            key=lambda item: int(item["id"])
        )

        return [item["vector"] for item in vectors]

        '''
        result = []

        for item in vectors:
            result.append(
                item["vector"]
            )

        return result
        '''