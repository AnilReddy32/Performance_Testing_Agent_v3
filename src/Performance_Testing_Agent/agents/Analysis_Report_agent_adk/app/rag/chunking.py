"""
Chunking strategies.

Two very different shapes of content need two different strategies:

1. Historical run results are already structured (one AnalysisOutput per
   job). We do NOT paragraph-chunk these -- we emit one small, dense chunk
   per API finding plus one for the overall summary, each carrying full
   metadata. This keeps retrieval precise ("give me POST /payments runs
   for this application/scenario") instead of fuzzy.

2. Static docs (SLA PDFs, runbooks, postmortems) are prose. We token-chunk
   them with overlap so a fact split across a sentence boundary is still
   findable, using tiktoken to size chunks the same way the embedding
   model sees them (character counts lie -- token counts don't).
"""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

CHUNK_SIZE_TOKENS = 400
CHUNK_OVERLAP_TOKENS = 60

_encoding = None


class _WhitespaceFallbackEncoding:
    """Offline fallback when tiktoken's BPE file can't be downloaded
    (e.g. no network to openaipublic.blob.core.windows.net). Approximates
    tokens as whitespace-split words -- close enough for chunk sizing,
    not used for anything that needs exact token counts. Production
    deployments with normal internet access will use real tiktoken."""

    def encode(self, text: str) -> List[str]:
        return text.split(" ")

    def decode(self, tokens: List[str]) -> str:
        return " ".join(tokens)


def _get_encoding():
    global _encoding
    if _encoding is not None:
        return _encoding
    try:
        import tiktoken
        _encoding = tiktoken.get_encoding("cl100k_base")
    except Exception as e:  # noqa: BLE001
        logger.warning("tiktoken BPE file unavailable (%s) -- falling back to "
                        "whitespace-based chunk sizing. Fine for offline dev; "
                        "production should have network access for real tiktoken.", e)
        _encoding = _WhitespaceFallbackEncoding()
    return _encoding


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE_TOKENS,
               overlap: int = CHUNK_OVERLAP_TOKENS) -> List[str]:
    """
    Token-aware recursive-ish splitter: splits on paragraph boundaries
    first, then greedily packs paragraphs into ~chunk_size-token windows
    with overlap, falling back to a hard token slice for any single
    paragraph that's bigger than chunk_size on its own (e.g. a giant
    table dumped as one paragraph).
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return []

    chunks: List[str] = []
    current: List[str] = []
    current_tokens = 0

    def flush():
        if current:
            chunks.append("\n\n".join(current))

    for para in paragraphs:
        para_tokens = len(_get_encoding().encode(para))

        if para_tokens > chunk_size:
            # Oversized paragraph: flush what we have, then hard-slice this one.
            flush()
            current, current_tokens = [], 0
            token_ids = _get_encoding().encode(para)
            for i in range(0, len(token_ids), chunk_size - overlap):
                window = token_ids[i:i + chunk_size]
                chunks.append(_get_encoding().decode(window))
            continue

        if current_tokens + para_tokens > chunk_size:
            flush()
            # start next chunk with overlap: carry the tail of the previous chunk
            overlap_text = chunks[-1] if chunks else ""
            overlap_tokens = _get_encoding().encode(overlap_text)[-overlap:] if overlap_text else []
            carried = _get_encoding().decode(overlap_tokens) if overlap_tokens else ""
            current = [carried, para] if carried else [para]
            current_tokens = len(_get_encoding().encode("\n\n".join(current)))
        else:
            current.append(para)
            current_tokens += para_tokens

    flush()
    return [c for c in chunks if c.strip()]


def build_historical_run_chunks(analysis_output: dict) -> List[dict]:
    """
    Turns one AnalysisOutput into a list of {"id", "document", "metadata"}
    dicts ready to upsert into the historical_runs collection. Called by
    the Report Agent's ingest tool right after a report is finalized.
    """
    if analysis_output.get("data_quality_status") != "valid":
        return []  # never pollute the knowledge base with invalid runs

    job_id = analysis_output["job_id"]
    application = analysis_output["application"]
    scenario = analysis_output["scenario"]
    generated_at = analysis_output.get("generated_at")  # optional, set by caller if available

    chunks = []

    # One chunk per API finding -- this is what query_historical_metrics matches against.
    for f in analysis_output.get("api_findings", []):
        m = f.get("metrics", {})
        doc = (
            f"Application: {application} | Scenario: {scenario} | API: {f['api_name']}\n"
            f"Status: {f['status']} | Severity: {f['severity']}\n"
            f"avg_response_time={m.get('avg_response_time')}ms, "
            f"p95_response_time={m.get('p95_response_time')}ms, "
            f"max_response_time={m.get('max_response_time')}ms, "
            f"throughput={m.get('throughput')} req/s, "
            f"error_rate={m.get('error_rate_pct')}%, "
            f"http_status={m.get('http_status')}\n"
            f"Anomalies: {'; '.join(f.get('anomalies', [])) or 'none'}"
        )
        chunks.append({
            "id": f"run:{job_id}:{f['api_name']}",
            "document": doc,
            "metadata": {
                "doc_type": "historical_run",
                "job_id": job_id,
                "application": application,
                "scenario": scenario,
                "api_name": f["api_name"],
                "status": f["status"],
                "severity": f["severity"],
                "error_rate_pct": m.get("error_rate_pct", 0.0),
                "p95_response_time": m.get("p95_response_time", 0.0),
                "generated_at": generated_at or "",
            },
        })

    if analysis_output.get("summary"):
        summary_text = f"Application: {application} | Scenario: {scenario}\nSummary: {analysis_output['summary']}"
        infra = analysis_output.get("infra_health")
        security = analysis_output.get("security_summary")
        if infra:
            summary_text += f"\nInfra health: {infra.get('status')} (CPU={infra.get('cpu_usage')}%, Memory={infra.get('memory_usage')}%)"
        if security:
            summary_text += f"\nSecurity: {security.get('status')} (score={security.get('security_score')})"

        chunks.append({
            "id": f"run:{job_id}:summary",
            "document": summary_text,
            "metadata": {
                "doc_type": "historical_run_summary",
                "job_id": job_id,
                "application": application,
                "scenario": scenario,
                "api_name": "",
                "status": analysis_output.get("overall_status", ""),
                "severity": "",
                "error_rate_pct": 0.0,
                "p95_response_time": 0.0,
                "infra_status": infra.get("status", "") if infra else "",
                "security_status": security.get("status", "") if security else "",
                "generated_at": generated_at or "",
            },
        })

    return chunks


def build_static_doc_chunks(text: str, source_file: str, doc_type: str,
                             extra_metadata: Optional[dict] = None) -> List[dict]:
    """
    doc_type: "sla" | "runbook" | "postmortem" (or your own taxonomy).
    IDs are content-hash based (via chunk index + source file) so
    re-ingesting the same file is idempotent (upsert, not duplicate).
    """
    extra_metadata = extra_metadata or {}
    pieces = chunk_text(text)
    chunks = []
    for i, piece in enumerate(pieces):
        chunks.append({
            "id": f"doc:{source_file}:{i}",
            "document": piece,
            "metadata": {
                "doc_type": doc_type,
                "source_file": source_file,
                "chunk_index": i,
                **extra_metadata,
            },
        })
    return chunks
