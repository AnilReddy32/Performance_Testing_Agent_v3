"""
Retrieval layer.

Two retrieval strategies, matched to the two collections:

1. query_historical_metrics(): metadata-first retrieval with a fallback
   ladder. We want exact matches (same application+scenario+api_name)
   when they exist, but must not return zero results just because this
   is the first run of a brand-new scenario -- so we progressively relax
   the filter. Within whatever candidate set we get, we apply MMR
   (maximal marginal relevance) so we don't hand the LLM five near-
   identical "normal" runs and call it history -- we want relevant AND
   diverse examples (including the odd one out, if there is one).

2. query_knowledge_docs(): classic hybrid search over prose documents
   (SLA/runbook/postmortem). Combines BM25 (lexical, good for exact
   terms like "JWT" or "error_rate SLA") with vector similarity (semantic,
   good for paraphrases), fused with Reciprocal Rank Fusion -- a standard,
   well-understood way to combine heterogeneous rankers without having to
   hand-tune a weighting between two different score scales.

retrieve_context() is the single function the Analysis Agent's
`retrieve_historical_context` tool calls; it wraps both.
"""

import logging
import math
from typing import List, Optional

import numpy as np
from rank_bm25 import BM25Okapi

from .embeddings import get_embedding_function
from .vector_store import get_historical_runs_collection, get_knowledge_docs_collection

_query_embedder = None


def _embed_query(text: str) -> List[float]:
    """Embeds a single query string using the same embedding function the
    collections were built with (kept as a module-level singleton so we
    don't re-instantiate an OpenAI client per call)."""
    global _query_embedder
    if _query_embedder is None:
        _query_embedder = get_embedding_function()
    return _query_embedder([text])[0]

logger = logging.getLogger(__name__)

RRF_K = 60  # standard constant for reciprocal rank fusion
MMR_LAMBDA = 0.7  # relevance vs. diversity trade-off (1.0 = pure relevance)


# ---------------------------------------------------------------------------
# Historical run retrieval
# ---------------------------------------------------------------------------

def _cosine_sim(a: List[float], b: List[float]) -> float:
    a, b = np.array(a), np.array(b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1e-8
    return float(np.dot(a, b) / denom)


def _mmr_select(query_embedding: List[float], candidates: List[dict], top_k: int,
                 lambda_param: float = MMR_LAMBDA) -> List[dict]:
    """candidates: list of {"embedding": [...], ...}. Returns top_k reordered for diversity."""
    if len(candidates) <= top_k:
        return candidates

    selected, remaining = [], candidates[:]
    while remaining and len(selected) < top_k:
        best_score, best_idx = -math.inf, 0
        for i, cand in enumerate(remaining):
            relevance = _cosine_sim(query_embedding, cand["embedding"])
            diversity_penalty = max(
                (_cosine_sim(cand["embedding"], s["embedding"]) for s in selected),
                default=0.0,
            )
            score = lambda_param * relevance - (1 - lambda_param) * diversity_penalty
            if score > best_score:
                best_score, best_idx = score, i
        selected.append(remaining.pop(best_idx))
    return selected


def query_historical_metrics(application: str, scenario: str, api_name: str,
                              top_k: int = 5) -> dict:
    """
    Fallback ladder: exact (application+scenario+api_name) -> drop scenario
    -> drop api_name -> application only. Stops relaxing as soon as a level
    returns at least one result, so the caller always knows exactly how
    comparable the returned history actually is (see "match_level").
    """
    collection = get_historical_runs_collection()
    query_text = f"{application} {scenario} {api_name} performance test run history"

    filters_ladder = [
        ("exact", {"$and": [{"application": application}, {"scenario": scenario}, {"api_name": api_name}]}),
        ("same_application_and_api", {"$and": [{"application": application}, {"api_name": api_name}]}),
        ("same_application_and_scenario", {"$and": [{"application": application}, {"scenario": scenario}]}),
        ("same_application_only", {"application": application}),
    ]

    for match_level, where in filters_ladder:
        try:
            result = collection.query(
                query_texts=[query_text],
                n_results=max(top_k * 3, top_k),  # overfetch for MMR to select from
                where=where,
                include=["documents", "metadatas", "embeddings", "distances"],
            )
        except Exception as e:  # noqa: BLE001
            logger.error("Historical query failed at level %s: %s", match_level, e)
            continue

        docs = result.get("documents", [[]])[0]
        if not docs:
            continue  # nothing at this level, relax further

        metadatas = result["metadatas"][0]
        embeddings = result["embeddings"][0]
        distances = result["distances"][0]

        candidates = [
            {"document": d, "metadata": m, "embedding": e, "distance": dist}
            for d, m, e, dist in zip(docs, metadatas, embeddings, distances)
        ]

        query_embedding = _embed_query(query_text)
        diverse = _mmr_select(query_embedding, candidates, top_k)

        # Recency tie-break within the diverse set: newer runs first among near-equal relevance
        diverse.sort(key=lambda c: c["metadata"].get("generated_at", ""), reverse=True)

        return {
            "available": True,
            "match_level": match_level,
            "results": [{"text": c["document"], "metadata": c["metadata"]} for c in diverse],
        }

    return {"available": False, "match_level": "none", "results": [],
            "note": f"No historical runs found for application='{application}' at any filter level."}


# ---------------------------------------------------------------------------
# Static knowledge doc retrieval (hybrid BM25 + vector, RRF fusion)
# ---------------------------------------------------------------------------

_bm25_cache = {"count": -1, "index": None, "ids": None, "docs": None, "metas": None}


def _get_bm25_index(collection):
    """
    Rebuilds the BM25 index from the collection whenever its size changes.
    Fine for a knowledge base in the hundreds-to-low-thousands of chunks
    (typical for SLA/runbook/postmortem corpora). For a much larger corpus,
    swap this for a persisted BM25/inverted index (e.g. OpenSearch/Elastic)
    instead of rebuilding in-process.
    """
    count = collection.count()
    if _bm25_cache["count"] == count and _bm25_cache["index"] is not None:
        return _bm25_cache

    all_data = collection.get(include=["documents", "metadatas"])
    ids, docs, metas = all_data["ids"], all_data["documents"], all_data["metadatas"]
    tokenized = [d.lower().split() for d in docs]
    index = BM25Okapi(tokenized) if tokenized else None

    _bm25_cache.update({"count": count, "index": index, "ids": ids, "docs": docs, "metas": metas})
    return _bm25_cache


def _reciprocal_rank_fusion(rankings: List[List[str]], k: int = RRF_K) -> List[str]:
    """rankings: list of ranked id-lists (best first). Returns fused ranking (best first)."""
    scores = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return [doc_id for doc_id, _ in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)]


def query_knowledge_docs(query_text: str, doc_types: Optional[List[str]] = None,
                          top_k: int = 5) -> dict:
    collection = get_knowledge_docs_collection()
    if collection.count() == 0:
        return {"available": False, "results": [], "note": "Knowledge base is empty."}

    where = {"doc_type": {"$in": doc_types}} if doc_types else None

    # --- Vector search branch ---
    vector_result = collection.query(
        query_texts=[query_text], n_results=min(20, collection.count()),
        where=where, include=["documents", "metadatas"],
    )
    vector_ids = vector_result["ids"][0]
    vector_docs = {i: d for i, d in zip(vector_ids, vector_result["documents"][0])}
    vector_metas = {i: m for i, m in zip(vector_ids, vector_result["metadatas"][0])}

    # --- BM25 branch ---
    bm25_cache = _get_bm25_index(collection)
    bm25_ranked_ids: List[str] = []
    if bm25_cache["index"] is not None:
        scores = bm25_cache["index"].get_scores(query_text.lower().split())
        ranked = sorted(zip(bm25_cache["ids"], scores), key=lambda x: x[1], reverse=True)
        candidate_ids = set(vector_ids)  # keep BM25 candidates aligned to the same filtered pool when possible
        bm25_ranked_ids = [doc_id for doc_id, score in ranked if score > 0][:20]
        if where:  # if we filtered by doc_type for vector search, apply the same filter to BM25 results
            id_to_meta = dict(zip(bm25_cache["ids"], bm25_cache["metas"]))
            allowed = set(doc_types)
            bm25_ranked_ids = [i for i in bm25_ranked_ids if id_to_meta.get(i, {}).get("doc_type") in allowed]

    fused_ids = _reciprocal_rank_fusion([vector_ids, bm25_ranked_ids])[:top_k]

    # Resolve text/metadata for fused ids (some may only be in the BM25 branch)
    id_to_doc = {**dict(zip(bm25_cache["ids"], bm25_cache["docs"])), **vector_docs}
    id_to_meta = {**dict(zip(bm25_cache["ids"], bm25_cache["metas"])), **vector_metas}

    results = [{"text": id_to_doc[i], "metadata": id_to_meta[i]} for i in fused_ids if i in id_to_doc]
    return {"available": bool(results), "results": results}


# ---------------------------------------------------------------------------
# Combined entry point used by the Analysis Agent
# ---------------------------------------------------------------------------

def retrieve_context(application: str, scenario: str, api_name: str,
                      anomaly_text: Optional[str] = None, top_k: int = 5) -> dict:
    """
    Called by app/agents/analysis/tools.py::retrieve_historical_context.
    Returns both comparable historical runs and any related SLA/runbook/
    postmortem content relevant to the current anomaly, if one is given.
    """
    historical = query_historical_metrics(application, scenario, api_name, top_k=top_k)

    docs_query = anomaly_text or f"{application} {api_name} performance SLA and known issues"
    docs = query_knowledge_docs(docs_query, top_k=top_k)

    return {"historical_runs": historical, "related_docs": docs}
