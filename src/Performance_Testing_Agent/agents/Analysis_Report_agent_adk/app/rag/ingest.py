"""
Ingestion pipeline for the RAG knowledge base.

Two entry points:
- ingest_historical_run(analysis_output): called automatically by the
  Report Agent right after it finalizes a report (closed loop). Upserts
  are idempotent on job_id + api_name, so re-running a job's report
  doesn't create duplicate history.
- ingest_static_document(path, doc_type, metadata): for SLA policies,
  runbooks, incident postmortems. Point it at a PDF or .txt/.md file.
  Also idempotent (upsert by source_file + chunk_index).

ingest_knowledge_base_dir() batch-ingests every file dropped into
knowledge_base/, inferring doc_type from a filename prefix convention
(sla_*, runbook_*, postmortem_*) -- adjust to your naming scheme.
"""

import logging
import os
from typing import Optional

from .chunking import build_historical_run_chunks, build_static_doc_chunks
from .vector_store import get_historical_runs_collection, get_knowledge_docs_collection

logger = logging.getLogger(__name__)

KNOWLEDGE_BASE_DIR = os.environ.get("KNOWLEDGE_BASE_DIR", "knowledge_base")


def _extract_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        import pdfplumber
        parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                if text.strip():
                    parts.append(text)
        return "\n\n".join(parts)
    elif ext in (".txt", ".md"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type for ingestion: {ext}")


def ingest_historical_run(analysis_output: dict) -> dict:
    """
    Called by the Report Agent as the final step of the report flow.
    Returns a small summary dict (never raises on empty/invalid input --
    an invalid run simply produces zero chunks, which is correct: we
    don't want bad data poisoning future historical comparisons).
    """
    chunks = build_historical_run_chunks(analysis_output)
    if not chunks:
        logger.info("No chunks to ingest for job_id=%s (invalid or empty analysis).",
                     analysis_output.get("job_id"))
        return {"ingested": 0, "job_id": analysis_output.get("job_id")}

    collection = get_historical_runs_collection()
    collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["document"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )
    logger.info("Ingested %d historical-run chunks for job_id=%s.",
                len(chunks), analysis_output.get("job_id"))
    return {"ingested": len(chunks), "job_id": analysis_output.get("job_id")}


def ingest_static_document(path: str, doc_type: str,
                            extra_metadata: Optional[dict] = None) -> dict:
    text = _extract_text(path)
    if not text.strip():
        logger.warning("No extractable text in %s -- skipping.", path)
        return {"ingested": 0, "source_file": path}

    chunks = build_static_doc_chunks(
        text=text, source_file=os.path.basename(path),
        doc_type=doc_type, extra_metadata=extra_metadata,
    )
    if not chunks:
        return {"ingested": 0, "source_file": path}

    collection = get_knowledge_docs_collection()
    collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["document"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )
    logger.info("Ingested %d chunks from %s (doc_type=%s).", len(chunks), path, doc_type)
    return {"ingested": len(chunks), "source_file": path}


# filename prefix -> doc_type, adjust to your naming convention
_PREFIX_MAP = {"sla": "sla", "runbook": "runbook", "postmortem": "postmortem", "incident": "postmortem"}


def ingest_knowledge_base_dir(directory: str = KNOWLEDGE_BASE_DIR) -> dict:
    """Batch-ingests every .pdf/.txt/.md file in `directory`. Infers
    doc_type from the filename prefix before the first underscore, e.g.
    'sla_payments_2026.pdf' -> doc_type 'sla'. Falls back to 'general'."""
    if not os.path.isdir(directory):
        logger.warning("Knowledge base directory %s does not exist.", directory)
        return {"files_processed": 0, "total_chunks": 0}

    total_chunks = 0
    files_processed = 0
    for fname in os.listdir(directory):
        if not fname.lower().endswith((".pdf", ".txt", ".md")):
            continue
        prefix = fname.split("_", 1)[0].lower()
        doc_type = _PREFIX_MAP.get(prefix, "general")
        result = ingest_static_document(os.path.join(directory, fname), doc_type=doc_type)
        total_chunks += result["ingested"]
        files_processed += 1

    return {"files_processed": files_processed, "total_chunks": total_chunks}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    summary = ingest_knowledge_base_dir()
    print(summary)
