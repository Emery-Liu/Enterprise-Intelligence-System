# Enterprise Entity Extraction

## Overview

Entity Extraction is the first stage of the Enterprise Intelligence System. Its objective is to identify and extract valid enterprise entities from unstructured public information, including news articles, web content, and other textual sources.

Unlike generic Named Entity Recognition (NER), this module focuses specifically on extracting **valid company entities** that can be processed by downstream algorithms. Invalid entities such as personal names, product names, organization categories, abbreviations, or ambiguous mentions are filtered during the extraction process.

The extracted enterprise entities serve as the foundation for the subsequent **Relevance Matching** and **Taxonomy Classification** modules.

---

## Motivation

Public information is inherently noisy and contains multiple entity types. Simply applying a general-purpose NER model usually produces many false positives that are not suitable for enterprise intelligence analysis.

For example, an article may contain:

* Company names
* Personal names
* Product names
* Government agencies
* Investment institutions
* Industry terms

Only validated enterprise entities should be passed to the downstream pipeline.

This module is designed to improve the precision of enterprise discovery by combining entity extraction with enterprise-specific validation.

---

## Input
**Notice**: Current algorithm is designed for Chinese Markert, therefore current IO examples are presented in Chinese

The algorithm accepts textual information from multiple fields.

Example:

```json
{
    "title": str,
    "summary": str,
    "content": str
}
```

The text may originate from news articles, web pages, public reports, or other enterprise-related documents.

---

## Output

A list of validated enterprise names.

Example:

```json
{
    "companies": List[str]
}
```

If no valid enterprise entity is detected, [] is returned.


## What I Learned

- Learned that general-purpose NER models are insufficient for domain-specific entity extraction. Combined rule-based pattern matching with LLM-based validation to improve extraction accuracy.

- Learned that production-ready entity extraction requires more than name recognition, including entity quality validation, ambiguity filtering, noise handling, and structured output generation.

---

## Core Techniques

- FastAPI
- Regular Expressions
- Large Language Models (LLMs)

---

## Future Improvements

* Support multilingual enterprise extraction.
* Design a confidence scoring mechanism for extracted entities
* Incorporate domain-specific knowledge bases for enterprise validation.

---

## docker

```bash
cd enterprise-intelligence-system

docker build \
-f entity_extraction/Dockerfile \
-t entity-extraction .

docker run --rm \
  --name entity-extraction \
  --env-file .env \
  -p 100:100 \
  entity-extraction
```


## Local Test Run

```bash
uvicorn entity_extraction.src.main:app --host 0.0.0.0 --port 100
```