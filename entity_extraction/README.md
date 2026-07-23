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

During development, I found that general-purpose Named Entity Recognition (NER) models alone were insufficient for this task. So I chose to use rule-based pattern matching together with LLM-assisted validation to complete this unit.

Building an enterprise entity extraction pipeline suitable for production environments requires not only identifying organization names but also verifying entity quality, filtering out ambiguous mentions, handling noisy public information, and producing structured output that downstream algorithms can reliably use.

---

## Core Techniques

- FastAPI
- Regular Expressions
- Large Language Models (LLMs)

---

## Future Improvements

Potential future improvements include:

* Support multilingual enterprise extraction.
* Design a confidence scoring mechanism for extracted entities
* Incorporate domain-specific knowledge bases for enterprise validation.


## Test Run
```bash
uvicorn entity_extraction.src.main:app --host 0.0.0.0 --port 100
```