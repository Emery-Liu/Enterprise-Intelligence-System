# Enterprise Relevance Matching

## Overview

Enterprise Relevance Matching is the second stage of the Enterprise Intelligence System. Its objective is to determine whether a piece of public information is genuinely related to a target enterprise.

After enterprise entities are extracted, not every identified company is necessarily the primary subject of the document. This module leverages a Large Language Model (LLM) to perform semantic reasoning and decide whether the target enterprise is truly associated with the given information.

---

## Motivation

Enterprise names may appear in documents for many different reasons. A company can be the primary subject, a competitor, a supplier, a customer, or simply be mentioned as background information.

Passing every extracted enterprise to downstream systems introduces unnecessary noise and may lead to incorrect analysis.

This module improves the reliability of the pipeline by filtering out enterprise entities that are not genuinely related to the document.

---

## Input

The algorithm accepts a target enterprise together with the corresponding textual information.

**Notice**: Current algorithm is designed for Chinese Markert, therefore current IO examples are presented in Chinese

```json
{
    "enterprise_name": str,
    "title": str,
    "summary": str,
    "content": str
}
```

---

## Output

A binary relevance decision.

Example:

```json
{
    "related": bool
}
```

---

## Core Techniques

- Prompt Engineering
- LLM-based Semantic Reasoning
- Structured JSON Output

---

## What I Learned

- Learned that enterprise relevance assessment requires semantic understanding beyond simple keyword matching.

- Learned that clear prompt design and structured output constraints can significantly improve the consistency and reliability of LLM-based decisions.
---

## Future Improvements

Potential future improvements include:

- Support multilingual enterprise relevance matching.
- Reduce inference latency through lightweight pre-filtering.

---

## docker

```bash
cd enterprise-intelligence-system

docker build \
-f relevance_matching/Dockerfile \
-t relevance_matching .

docker run --rm \
  --name relevance_matching \
  --env-file .env \
  -p 1000:1000 \
  relevance_matching
```

---

## Test Run

```bash
uvicorn relevance_matching.src.main:app --host 0.0.0.0 --port 1000
```