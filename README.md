# ANZ_Performance_testing_agents
# ANZ_Performance_testing_agents
## RAG Knowledge Base Setup

The Analysis Agent's historical-context lookup (`retrieve_historical_context`) and the
Report Agent's closed-loop ingestion (`ingest_report_to_knowledge_base`) depend on a local
ChromaDB vector store that must be seeded once before first use.

### One-time setup

1. Install RAG dependencies (not in the main project's `uv.lock`):uv pip install chromadb rank_bm25 numpy
2. Set `OPENAI_API_KEY` in your terminal session before ingesting — otherwise embeddings
   fall back to a deterministic hash (poor retrieval quality):set OPENAI_API_KEY=sk-...
3. Add absolute paths to the project-root `.env` (relative paths break if `adk web` is run
   from a different working directory later):VECTOR_DB_DIR=<absolute path>\Analysis_Report_agent_adk\vector_db
KNOWLEDGE_BASE_DIR=<absolute path>\Analysis_Report_agent_adk\knowledge_base

4. From inside this folder, run:python -m app.rag.ingest
   Confirm the output does **not** show `OPENAI_API_KEY not set`.

Add new `.txt`/`.md`/`.pdf` documents to `knowledge_base/` and re-run step 4 to update retrieval content.
