# Taxonomy Classification

## Overview

Enterprise Industry Chain Classification is the third stage of the Enterprise Intelligence System. Its objective is to determine which node(s) of a predefined industry taxonomy tree a given enterprise genuinely belongs to, based on multi-source public information.

Given the diverse evidence related to the company, this module consolidates the evidence to map the company to one or more leaf node paths within a large, fixed industry classification tree.

---

## Motivation

A single enterprise often operates across multiple business lines, and a flat single-label classification cannot capture this reality. At the same time, the taxonomy tree is too large to be passed to a Large Language Model in a single prompt — doing so would be costly in tokens and would make the model prone to selecting categories that do not actually exist in the tree.

This module addresses both problems by narrowing the search space with vector retrieval before invoking the LLM, and by constraining every LLM decision to the real children of the tree at each level, rather than asking the model to freely generate a category name.

---

## Input

**Notice**: Current algorithm is designed for Chinese Market, therefore current IO examples are presented in Chinese.

```json
{
    "company": str,
    "web_data_list": [
        {"link": str, "content": str}, ..
    ],
    "baike_data": {
        "link": str,
        "content": str
    },
    "yuqing_data_list": [
        {"link": str, "content": str}, ..
    ],
    "patent_data_list": [
        {"link": str, "content": str}, ..
    ],
    "project_data_list": [
        {"link": str, "content": str}, ..
    ]
}
```

Not every source is guaranteed to be present or non-empty; the algorithm treats missing or empty entries as absent evidence rather than failing.

---

## Output

A list of classification paths. Each path represents one branch of the taxonomy tree the enterprise is judged to belong to, together with a confidence score and the reasoning produced at each level of the tree.

Example:

```json
{
    "paths": [
        {
            "path": List[str],
            "score": num,
            "reasoning_chain": List[str]
        },
        {
            "path": List[str],
            "score": num,
            "reasoning_chain": List[str]
        }
    ]
}
```

---

## Core Techniques

- Large Language Models (LLM)
- Retrieval-Augmented Generation (RAG)
- BGE-M3 Embeddings
- FAISS Approximate Nearest Neighbor Search
- Hierarchical Multi-label Classification
- SimHash
- Prompt Engineering

---

## What I Learned

Building this module made clear that hallucination in structured classification tasks is best prevented by construction rather than by correction. Instead of letting the LLM choose freely from the full taxonomy and then validating the result, restricting the model's choices at each step to only the real children of the current node made incorrect outputs structurally impossible in most cases, with tree-based validation serving only as a final safety net rather than the primary defense.

I also learned to reason carefully about which parts of an asynchronous pipeline actually need to be asynchronous. Only operations with genuine network I/O (LLM calls, embedding calls) benefit from `async/await`

Finally, working through the deployment constraints of this module — balancing dependency size, offline build environments, and version-specific package indexes — taught me that infrastructure limitations sometimes call for reconsidering an architectural decision (in this case, moving from a locally hosted embedding model to an internally provided embedding API) rather than repeatedly working around the same constraint.
---

## Future Improvements

Potential future improvements include:

## Future Improvements

- Improve output stability by introducing path reranking system
- Further optimize retrieval quality by refining enterprise profile generation and candidate retrieval strategies.
- Explore more reliable structured output mechanisms to reduce failures caused by malformed LLM-generated JSON.

---

## Test Run

```bash
uvicorn main:app --host 0.0.0.0 --port 10
```