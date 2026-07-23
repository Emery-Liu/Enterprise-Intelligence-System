# Enterprise Intelligence System

An end-to-end enterprise intelligence system for extracting enterprise information from unstructured public data, verifying enterprise relevance, and classifying enterprises into a hierarchical industry taxonomy.

The system combines Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and FAISS vector retrieval to process multi-source enterprise information in a reliable and scalable pipeline.

---

## Overview

The Enterprise Intelligence System consists of three major stages:

1. **Entity Extraction**
   - Extract enterprise entities from unstructured text such as news articles and web pages.

2. **Enterprise Relevance Check**
   - Determine whether the extracted enterprise is genuinely the subject of the given content.

3. **Taxonomy Classification**
   - Classify enterprises into one or more paths of a predefined hierarchical industry taxonomy using retrieval-assisted reasoning.

Together, these stages transform noisy public information into structured enterprise intelligence suitable for downstream analytics and knowledge graph construction.

---

## System Pipeline

```
                Public Information
        (News / Web / Patents / Projects)
                        │
                        ▼
                Entity Extraction
                        │
                        ▼
            Enterprise Relevance Check
                        │
                        ▼
              Taxonomy Classification
                        │
                        ▼
          Structured Enterprise Knowledge
```

---

## Key Technologies

- Large Language Models (LLMs)
- Retrieval-Augmented Generation (RAG)
- FAISS Vector Search
- Hierarchical Multi-label Classification
- FastAPI
- Pydantic
- asyncio

---

## Repository Structure

```
.
├── entity_extraction/
├── relevance_check/
├── taxonomy_classification/
├── requirements.txt
└── README.md
```

Each module contains its own implementation and documentation.

---

## Getting Started

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

Create a `.env` file based on `.env.example` and configure the required API endpoints and credentials.


---

## Documentation

Detailed documentation for each module is available in the corresponding subdirectory.

- Entity Extraction
- Enterprise Relevance Check
- Taxonomy Classification

