"""
Shared ChromaDB persistent client + collection accessors.

Two collections, deliberately kept separate rather than one mixed
collection:

- "historical_runs": one chunk per API finding from completed test jobs.
  Small, structured, metadata-heavy (job_id, application, scenario,
  api_name, status, severity, timestamp). Queried with strict metadata
  pre-filters -- these are apples-to-apples comparisons, not fuzzy search.

- "knowledge_docs": chunks of SLA policies, runbooks, incident
  postmortems. Larger, prose-heavy chunks. Queried with hybrid
  (BM25 + vector) search since questions here are more open-ended
  ("what's our error-rate SLA for payments?").

Keeping them separate means each can have its own chunking strategy and
retrieval logic without one polluting the other's ranking.
"""

import os
import chromadb

from .embeddings import get_embedding_function

VECTOR_DB_DIR = os.environ.get("VECTOR_DB_DIR", "vector_db")

_client = None


def get_client() -> "chromadb.ClientAPI":
    global _client
    if _client is None:
        os.makedirs(VECTOR_DB_DIR, exist_ok=True)
        _client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    return _client


def get_historical_runs_collection():
    return get_client().get_or_create_collection(
        name="historical_runs",
        embedding_function=get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )


def get_knowledge_docs_collection():
    return get_client().get_or_create_collection(
        name="knowledge_docs",
        embedding_function=get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )
