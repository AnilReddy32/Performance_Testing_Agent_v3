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

## Execution context and REAL-run safety (Phase 1)

Requests to create or run a k6 performance-test script select `REAL`
execution, including API chat requests without a catalog case. A complete
trusted workload profile and passing safety preflight are still required;
missing profile values are requested rather than guessed or simulated.
Supply that profile by loading a trusted catalog case in ADK Web or through
the API's execution context; free-form workload values are not converted into
trusted profile data automatically.
Unless the request explicitly says not to execute, a k6 script request runs
the test and captures its native report. JMeter and Gatling requests continue
to use the simulated path.
After a completed REAL k6 run, the orchestrator runs monitoring, security,
analysis, and report in that order; the final PDF references the generated
native report and raw artifacts. If execution is blocked, fails, or needs
profile input, downstream stages do not consume simulated or stale results.

In ADK Web or the chat API, select a catalog case directly in the request,
for example: `Run test case PTC-012, monitor it, analyze the combined
results, and generate the final PDF report.` The orchestrator binds the ID
to the catalog profile before execution, so do not repeat its workload
fields in the prompt. Each PTC/WTC entry must exist in the catalog; a request
with multiple IDs is rejected as ambiguous. In ADK Web, a new explicit case
can replace a prior job only when that job is not running.

The workload profile is a typed view of the catalog's execution inputs:
`tool`, `target_url`, `environment` (initially `mock_api`), `endpoint`,
`method`, `payload_template`, `expected_status_code`, `p95_threshold_ms`,
`users`, `duration_seconds`, `ramp_up_seconds`, `max_rps`, and
`credentials_ref`. Real k6 preparation requires an explicit p95 threshold;
the existing `expected_response_time_ms` is not assumed to mean p95. Missing
values are reported as required user input. Use `credentials_ref: "none"`
when the approved endpoint does not require credentials. Store credential
references only; never put secret values in catalog JSON or prompts.

Every REAL workload must provide an explicit positive `max_rps`. The reviewed
k6 script and runner both enforce that rate ceiling; no unbounded loopback
load is started when the profile omits it.

Real-run preflight defaults are intentionally limited to the local mock API:

```dotenv
REAL_EXECUTION_ENABLED=false
REAL_EXECUTION_ALLOWED_HOSTS=localhost,127.0.0.1
REAL_EXECUTION_ALLOWED_PORTS=8000
REAL_EXECUTION_MAX_USERS=500
REAL_EXECUTION_MAX_DURATION_SECONDS=500
REAL_EXECUTION_MAX_RAMP_UP_SECONDS=90
EXECUTION_ARTIFACTS_ROOT=src/generated_scripts/artifacts
```

Unset safety limits use the defaults above; malformed settings block REAL
preflight. The initial target check requires an allowlisted host, loopback DNS
resolution, and an allowed port. The real runner must repeat target validation
for every redirect before following it. Add a non-local hostname only after
the test environment and workload have been explicitly approved.

The safe mock API used for local k6 validation is
`Performance_Testing_Agent.mock_api:app`. Start it bound to loopback only:

```bash
PYTHONPATH=src .venv/bin/python -m uvicorn \
  Performance_Testing_Agent.mock_api:app \
  --host 127.0.0.1 --port 8000
```

Validate and run a prepared local k6 script by setting its `BASE_URL`:

```bash
JOB_ID=JOB-0123456789abcdef0123456789abcdef
SCRIPT_PATH="src/generated_scripts/artifacts/$JOB_ID/k6_PTC_011_Local_Mock_Payment_API_k6_Script_Generation.js"
k6 inspect -e BASE_URL=http://localhost:8000 "$SCRIPT_PATH"
k6 run -e BASE_URL=http://127.0.0.1:8000 "$SCRIPT_PATH"
```

Replace the example `JOB_ID` with the prepared run's job ID.

Each request receives a generated `JOB-<uuid>` and a planned directory under
`src/generated_scripts/artifacts/<job_id>/`. Phase 1 defines the job status
and artifact-manifest contract. REAL k6 scripts are named from the test-case
ID and title (or the requested scenario when no catalog title is available).
An explicit run request validates the reviewed script, executes k6, and
stores raw samples, a normalized metrics JSON file, a five-second time
series, the k6 summary export, runner logs, and the native HTML report in
that job's artifact directory. An explicit request not to execute prepares
the named script without running it.

### Phase 2, step 1: Real k6 script preparation

For k6 requests with passing REAL preflight, the Test Execution Agent bypasses
the LLM planner and writes a titled script into that job's artifact directory
from a deterministic template. The profile's total
`duration_seconds` includes ramp-up and ramp-down; the hold stage uses the
remaining time. The script checks the configured HTTP status, applies the
catalog's explicit `p95_threshold_ms`, and enforces the existing 1% error-rate
threshold. POST/PUT/PATCH JSON bodies may use `{{__VU}}` and `{{__ITER}}`
placeholders for per-iteration values. The current runner accepts only
`credentials_ref: "none"`; authenticated runs fail closed until a secret
reference provider is configured. No secret is written into the script.
Requests disable redirect following, and the runner revalidates the target
before execution. A k6 script request executes by default; an explicit
instruction not to run it stops after script preparation. Phase 2 step 2
validated the script with k6 and ran it against the loopback-only mock API.

### Phase 2, step 3: Real k6 runner and artifacts

For REAL k6 requests, the Test Execution Agent verifies the script still
matches the deterministic template, runs `k6 inspect`, and executes k6
with the profile's `max_rps`. A completed execution stores raw JSON samples,
the native k6 JSON summary, normalized 13-field metrics, a five-second CSV
time series, the self-contained native HTML dashboard report, and runner
logs. A k6 threshold breach is a completed run with failing metrics; tool,
script, timeout, or artifact-generation failures are execution errors.
Explicit no-execution requests stop after preparing the titled script.

### Phase 3, steps 1-2: Runtime sampling and measurement provenance

During a REAL k6 run, a concurrent `psutil` sampler writes timestamped
CPU and memory samples to `*_runtime_samples.csv`. These measurements are
host-wide readings from the machine running the load generator; they are
not target-application resource metrics. The five-second k6 time series
contains client-observed HTTP request, latency, and throughput measurements,
not target CPU/memory. `*_measurement_metadata.json` records these scopes
and sources explicitly. Database connections are marked as not collected
until a target-specific telemetry provider is configured; they are never
filled with simulated values in the REAL execution artifacts.

### Phase 4, step 1: Shared time-series schema and alignment

Every REAL run also writes `*_aligned_time_series.csv` using schema version
`1.0`. Its columns are:

`timestamp, elapsed_seconds, bucket_duration_seconds, requests,
successful_requests, failed_requests, avg_response_time_ms, throughput_rps,
cpu_avg_percent, cpu_peak_percent, memory_avg_percent, memory_peak_percent,
execution_data_source, execution_measurement_scope, monitoring_data_source,
monitoring_measurement_scope, target_resource_metrics`

All timestamps are timezone-aware UTC. Both data sources are aligned to
half-open five-second windows relative to `k6_run_window.started_at`
(`elapsed_seconds` 0, 5, 10, ...), not wall-clock epoch boundaries or the
sampler's own start. The final window is shortened to the actual run end.
CPU and memory are the average and peak of psutil readings whose timestamps
fall in that window. Request counts and latency come from k6 samples in the
same window; throughput is requests divided by the actual window duration.
An empty execution window has zero request counts and zero throughput, while
latency or monitoring values with no observation are blank. Every row
identifies each source and measurement scope; host-generator readings are
never labeled target-resource metrics.

### Phase 4, step 2: Deterministic time-series analysis

The Analysis Agent reads only the current REAL job's aligned CSV from its
validated artifact manifest and checks the schema metadata, UTC timestamps,
run-relative bucket ordering, counts, throughput, finite values, and source
scopes before calculating trends. It reports first-to-last bucket latency and
throughput changes, overall and rising per-bucket error rates, peak and
average observed load, and Pearson latency/resource correlations when at
least three paired buckets with non-constant values are available.

Resource correlations are explicitly limited to load-generator host CPU and
memory; they do not imply target-resource behavior or causation. Post-ramp
degradation compares fully ramp-up buckets with post-ramp buckets from the
trusted workload profile. It is flagged when mean post-ramp latency increases
by more than 20% or mean error rate increases by more than 1 percentage point.
When there are too few paired observations or a metric has no variance, its
correlation is left undefined; insufficient ramp/post-ramp windows are
identified instead of guessed. Missing latency data or unavailable/invalid
aligned artifacts produce an unavailable result rather than estimates.
Actionable deterministic findings contribute to the overall analysis status.

### Phase 4, step 3: Analysis findings and provenance

`AnalysisOutput.time_series_analysis` retains the deterministic findings and
their provenance. REAL findings identify `execution_mode: REAL` and the
contributing data sources; the result identifies k6 client-observed traffic
and, when available, psutil load-generator-host samples. It explicitly marks
these as non-target resource measurements. Post-ramp findings also identify
the trusted workload profile used for the comparison.

SIMULATED runs are explicitly labeled `SIMULATED` with
`simulated_estimate` provenance and return no measured time-series findings.
They are not converted into synthetic time-series values. If a REAL artifact
is missing or invalid, the result remains REAL but unavailable; it never
falls back to simulated data. The structured findings and provenance are
preserved by analysis finalization in the result passed downstream.

The existing Monitoring Agent tool now reads the REAL run's sample artifact
without changing its delegation or state-output flow. It reports average and
peak load-generator CPU/memory, and labels k6 latency/throughput as
client-observed traffic. Missing or invalid REAL samples are reported as
unavailable, never replaced with estimates. SIMULATED runs retain the existing
deterministic simulator and label its values as simulated estimates. Source
and measurement scope are carried into analysis and the report.

### Phase 5, step 1: Execution details in the final report

The analysis result carries the execution mode, a non-secret workload
profile, the job artifact directory, and artifact references from the
execution manifest. The Report Agent includes these values in an
`Execution Profile and Artifacts` section. Credentials references and
payload templates are excluded from the published profile. Native/raw
artifact packaging and PDF links are completed in Step 2; API access and
retention behavior remain for Step 4.

### Phase 5, step 2: Native report and raw-result package

For a REAL run whose execution manifest contains both the native k6 HTML
report and raw JSON results, report generation creates
`<job_id>_native_report.zip` in that job's artifact directory. The archive
contains the native report and raw results in separate folders. The
consolidated PDF links to the HTML report, raw JSON, and ZIP; it does not
embed the interactive dashboard. Artifact references are resolved and
validated against the current job directory before packaging.

### Phase 5, step 3: PDF time-series graphs

For analyzed REAL runs, the PDF includes measured latency, throughput, and
load-generator host CPU graphs from the aligned five-second series. CPU is
clearly labeled as a load-generator measurement, not target-resource data.
SIMULATED or unavailable runs do not produce graphs from invented data.

### Phase 5, step 4: API artifact access and retention

The `/chat` response includes an `execution_job.artifacts` map from artifact
keys to downloadable URLs, along with the UTC expiration time and retention
duration. The corresponding `GET /artifacts/{job_id}/{artifact_key}` endpoint
serves only files registered in that job's artifact manifest. Downloads
require an `Authorization: Bearer <token>` header. Configure
`ARTIFACT_ACCESS_TOKEN` with a high-entropy secret of at least 32 characters;
downloads fail closed when it is unset or too short. Configure
`ARTIFACT_PUBLIC_BASE_URL` to return absolute URLs suitable for API consumers
and PDF links; if unset, references are relative to the API origin.

Artifact manifests use schema version 1.0 and default to 30 days of retention,
configurable with `ARTIFACT_RETENTION_DAYS` (positive whole days). Startup
and hourly cleanup delete expired, manifest-backed `JOB-<uuid>` artifact
directories. Expired downloads return HTTP 410; unknown/unregistered
artifacts return HTTP 404. Responses are private and non-cacheable. The
current authorization is one shared bearer token for the service and does
not provide per-user or per-tenant artifact ACLs; deploy behind an
identity-aware gateway if callers need individual authorization.

### Running PTC-012 from ADK web

The ADK web entry point is `adk_web/performance_testing_agent`. Start the
local mock API in one terminal:

```bash
PYTHONPATH=src .venv/bin/python -m uvicorn \
  Performance_Testing_Agent.mock_api:app \
  --host 127.0.0.1 --port 8000
```

In a second terminal, start ADK web with REAL execution explicitly enabled:

```bash
PYTHONPATH=src REAL_EXECUTION_ENABLED=true \
  .venv/bin/adk web --port 8765 adk_web
```

Open `http://127.0.0.1:8765`, select `performance_testing_agent`, and submit:

> Run test case PTC-012 against the local mock API. Analyze the results and
> generate the final PDF report.

The explicit catalog ID loads the trusted REAL profile into the ADK session;
the prompt's run request authorizes execution. This test is limited to
`localhost:8000`, one virtual user, 5 RPS, and 40 seconds. k6 must be
available on `PATH`, and the configured model credentials must be available
through the project `.env` or shell environment.

The PDF is written under `src/data/reports/` and copied into the job artifact
directory. REAL reports include measured latency, throughput, and
load-generator CPU charts, with API links to the native HTML dashboard, raw
k6 results, and their ZIP package. The generated script, raw/normalized
results, monitoring samples, time series, native report, and consolidated
PDF are in `src/generated_scripts/artifacts/<job_id>/`.

For a generation-only check, select PTC-011 and ask:

> Generate the k6 script for test case PTC-011 only. Do not run the test.

For execution and reporting, select PTC-012 as above. It is intentionally
capped at one virtual user, 5 RPS, and 40 seconds against the local mock.
Wait for the test-execution, monitoring, analysis, and report agents to
finish. Review the final response and open the consolidated PDF from the
ADK artifact panel or the job artifact directory. PDF artifact links require
the configured artifact bearer token when opened outside ADK; see the
artifact-access settings above.
