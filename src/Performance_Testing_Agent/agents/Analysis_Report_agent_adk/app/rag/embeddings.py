"""
Embedding function selection for the RAG layer.

Production path: OpenAI text-embedding-3-small (matches your tech stack
table). Dev/offline fallback: a deterministic hash-based embedding so the
ingestion/retrieval *pipeline* (chunking, filtering, ranking, fallback
ladders) can be built and tested without network access or an API key.

IMPORTANT: the hash-based fallback produces vectors with no real semantic
meaning -- cosine similarity between them is close to random. It exists
ONLY so code paths are exercisable in CI/local dev without hitting
OpenAI. Never rely on it for a real similarity judgment. It logs a loud
warning so nobody mistakes it for the real thing in production.
"""

import hashlib
import logging
import os
from typing import List

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = os.environ.get("RAG_EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIM = 1536  # text-embedding-3-small's native dimension


from chromadb import EmbeddingFunction


class DeterministicHashEmbeddingFunction(EmbeddingFunction):
    """Offline/dev-only stand-in. Same input -> same vector, so retrieval
    logic (filtering, top_k, dedup, MMR) can be exercised deterministically
    in tests. NOT semantically meaningful. Subclasses Chroma's
    EmbeddingFunction so embed_query() correctly falls back to __call__
    (some embedding models embed queries/documents differently -- ours
    doesn't need to)."""

    def __call__(self, input: List[str]) -> List[List[float]]:
        vectors = []
        for text in input:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            # Repeat/truncate the 32-byte digest out to EMBEDDING_DIM floats in [-1, 1]
            raw = (digest * (EMBEDDING_DIM // len(digest) + 1))[:EMBEDDING_DIM]
            vectors.append([(b - 127.5) / 127.5 for b in raw])
        return vectors

    def name(self) -> str:
        return "deterministic-hash-dev-fallback"


def get_embedding_function():
    """
    Returns a Chroma-compatible embedding function.

    Set OPENAI_API_KEY to use real embeddings (production). If it's
    missing, falls back to the deterministic dev stub and logs a warning
    -- this should never silently happen in a real deployment, so make
    sure your prod env / secrets manager sets the key.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
        return OpenAIEmbeddingFunction(api_key=api_key, model_name=EMBEDDING_MODEL)

    logger.warning(
        "OPENAI_API_KEY not set -- RAG layer is using the deterministic "
        "hash-based embedding fallback. Retrieval quality will be poor. "
        "This is only acceptable for local/offline development."
    )
    return DeterministicHashEmbeddingFunction()
