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

## Execution context and REAL-run safety (Phases 1–5)

Requests to create or run a k6 or JMeter performance-test script select `REAL`
execution, including API chat requests without a catalog case. A complete
trusted workload profile and passing safety preflight are still required;
missing profile values are requested rather than guessed or simulated.
Supply that profile by loading a trusted catalog case in ADK Web or through
the API's execution context; free-form workload values are not converted into
trusted profile data automatically.
Unless the request explicitly says not to execute, a k6 script request runs
the test and captures its native report under
`src/generated_scripts/k6 native reports/<job_id>/`, alongside its other
job artifacts. JMeter requests enter REAL-mode
preflight. After preflight passes, the agent generates a deterministic JMX
plan from the trusted profile and saves it under
`src/generated_scripts/Jmeter native reports/<job_id>/`. The plan includes the
HTTP target,
method, configured headers and JSON body, users, ramp-up, duration, and a
shared-thread-group throughput cap. `REAL_JMETER_MAX_RPS` sets the maximum
accepted JMeter rate (default `1000` requests/second). A generation-only
request stops after preparing the plan. An explicit JMeter run request also
executes that plan with the JMeter and Java executables found on `PATH`, in
non-GUI mode, with a bounded timeout and process-group cleanup. The job
directory receives the raw JTL results, JMeter log, normalized metrics, and
runner log. Missing dependencies and runner errors are REAL failures;
response/status and p95 threshold breaches remain completed REAL outcomes with
`thresholds_passed: false`. Header values are referenced as JMeter properties
so secrets are not written into the JMX file or command line. Native HTML
report generation runs from the JTL with JMeter's dashboard generator. The
dashboard is stored at
`src/generated_scripts/Jmeter native reports/<job_id>/jmeter_native_report/`;
the per-job directory contains the JMX plan, raw JTL, logs, metrics, and
dashboard ZIP. Open `jmeter_native_report/index.html` to view the dashboard.
The artifact manifest exposes the dashboard, raw JTL, and ZIP through
the authenticated `/artifacts/<job_id>/<artifact_key>` API. The final PDF links
to each item. REAL JMeter runs also create the shared five-second aligned
time-series files from current-job JTL samples and sample the load-generator
host with psutil while JMeter is running. CPU and memory are labeled as
load-generator measurements, not target telemetry. Request/error counts,
throughput, and latency percentiles flow into analysis from the JTL. Gatling
requests continue to use the simulated path.
After a completed REAL k6 or JMeter run, the orchestrator runs monitoring,
security, analysis, and report in that order. The k6 final PDF can reference
its native HTML report; JMeter's final PDF links to its native HTML dashboard
and raw JTL. If execution is blocked, fails, or needs profile input, downstream
stages do not consume simulated or stale results.

In ADK Web or the chat API, select a catalog case directly in the request,
for example: `Run test case PTC-012, monitor it, analyze the combined
results, and generate the final PDF report.` The orchestrator binds the ID
to the catalog profile before execution, so do not repeat its workload
fields in the prompt. Each PTC/WTC entry must exist in the catalog; a request
with multiple IDs is rejected as ambiguous. In ADK Web, a new explicit case
can replace a prior job only when that job is not running.

The same performance case ID can be run with either real runner by naming it
explicitly in the request, for example `Run test case PTC-001 using JMeter`
or `Run test case PTC-001 using k6`. The requested runner is selected for that
job; the URL, endpoint, method, payload, load limits, and thresholds continue
to come from the trusted catalog entry. The selected runner's safety preflight
is rerun before execution. If no runner is named, the catalog's configured
tool remains the default. Do not request both runners in one execution.

The workload profile is a typed view of the catalog's execution inputs:
`tool`, `target_url`, `environment` (`mock_api` or `external_api`), `endpoint`,
`method`, `payload_template`, `expected_status_code`, `p95_threshold_ms`,
`users`, `duration_seconds`, `ramp_up_seconds`, `max_rps`, and
`credentials_ref`. Real k6 preparation requires an explicit p95 threshold;
the existing `expected_response_time_ms` is not assumed to mean p95. Missing
values are reported as required user input. Use `credentials_ref: "none"`
when the approved endpoint does not require credentials. Store credential
references only; never put secret values in catalog JSON or prompts.

Every REAL workload must provide an explicit positive `max_rps`. The reviewed
k6 script and runner both enforce that rate ceiling. JMeter's generated plan
uses a shared-thread-group throughput timer bounded by `REAL_JMETER_MAX_RPS`.
Header environment variables referenced by `header_env` must be set for the
agent process; the runner passes them through a temporary private properties
file and removes it after execution. No REAL workload is started when the
profile omits its rate limit.

Real-run preflight defaults are intentionally limited to the local mock API:

```dotenv
REAL_EXECUTION_ENABLED=false
REAL_EXECUTION_EXTERNAL_TARGETS_ENABLED=false
REAL_EXECUTION_ALLOWED_HOSTS=localhost,127.0.0.1
REAL_EXECUTION_ALLOWED_PORTS=8000
REAL_EXECUTION_MAX_USERS=500
REAL_EXECUTION_MAX_DURATION_SECONDS=500
REAL_EXECUTION_MAX_RAMP_UP_SECONDS=90
REAL_JMETER_MAX_RPS=1000
K6_EXECUTION_ARTIFACTS_ROOT="src/generated_scripts/k6 native reports"
JMETER_EXECUTION_ARTIFACTS_ROOT="src/generated_scripts/Jmeter native reports"
```

Unset safety limits use the defaults above; malformed settings block REAL
preflight. Local `mock_api` targets must resolve only to loopback addresses.
External targets are disabled by default. To enable a specific approved HTTPS
API, set `REAL_EXECUTION_EXTERNAL_TARGETS_ENABLED=true`, add its exact hostname
to `REAL_EXECUTION_ALLOWED_HOSTS`, and add its HTTPS port to
`REAL_EXECUTION_ALLOWED_PORTS` (normally `443`). External DNS results must all
be public addresses. Keep the allowlist limited to systems you are authorized
to load test. Redirect following is disabled in the generated k6 request so a
redirect cannot send load to a second host. The runner repeats target
validation immediately before execution. For production deployments, enforce
the same destination policy with network egress controls as well.

#### Stored script reuse

For catalog test cases (`PTC-` / `WTC-` IDs), the reviewed REAL k6 or JMeter
script is stored once under `<artifact root>/_script_library/<tool>/<test case>/`
and copied into each later job folder instead of being rebuilt. A stored script
is reused only when a fingerprint of the full workload profile, the template's
source and the Python version still matches and its SHA-256 is intact, so any
change to the test case (users, duration, thresholds, target...) regenerates
the script and replaces the stored one. Each runner keeps its own stored script.
The target-allowlist/limit preflight is re-run on every reuse, and the runners
still rebuild and compare the script before executing it. Anything unexpected
falls back to building the script as before. Set `SCRIPT_REUSE_ENABLED=false`
to build a fresh script on every run.

### JMeter and Java installation, configuration, and native reports

REAL JMeter execution requires Apache JMeter and Java to be installed on the
machine running the agent, with both `jmeter` and `java` discoverable on
`PATH`. The generated JMX identifies JMeter 5.6.3. JMeter 5.6.x supports Java
8 or later; Java 17 or later is recommended by Apache. A JDK is recommended
when HTTPS certificate recording or Java development tools are needed. See
the [Apache JMeter installation and requirements guide](https://jmeter.apache.org/usermanual/get-started.html)
and [official download page](https://jmeter.apache.org/download_jmeter.cgi).

After installation, open a new terminal (or restart the agent process) and
confirm both commands resolve and print their versions:

```bash
jmeter --version
java -version
```

On macOS or Linux, add the JMeter `bin` directory to `PATH` if `jmeter` is
not found. Set `JAVA_HOME` to the installed JDK when Java is not automatically
detected. `JMETER_HOME` may be set to the JMeter installation directory when
the launcher cannot infer it. Restart FastAPI/ADK after changing these
environment variables so the agent process sees them. Missing JMeter or Java
is reported as a failed REAL run; the agent does not switch to simulated
results.

JMeter safety and workload settings use the same preflight controls as the
other REAL runner, plus `REAL_JMETER_MAX_RPS` (default `1000`). Configure
`REAL_EXECUTION_ENABLED=true` to permit REAL workloads. Local mock targets are
allowed by default only on loopback and port 8000. External targets require
`REAL_EXECUTION_EXTERNAL_TARGETS_ENABLED=true` and explicit host/port
allowlisting. `header_env` values name environment variables containing
secrets; set those variables in the agent process environment and never put
the secret values in the test catalog. The runner supplies these values via a
temporary private Java properties file and removes it after execution.

For each k6 job, the generated script, raw results, summary, normalized
metrics, runtime samples, time-series files, native report, and runner logs
are stored together under `src/generated_scripts/k6 native reports/<job_id>/`.
JMeter's JMX plan, raw JTL, logs, metrics, samples, native dashboard, and ZIP
are stored together under `src/generated_scripts/Jmeter native reports/<job_id>/`.
Open `jmeter_native_report/index.html` to view JMeter's dashboard. The
dashboard, raw JTL, and ZIP are listed in the job artifact manifest and are
downloadable from `/artifacts/<job_id>/native_report`,
`/artifacts/<job_id>/raw_results`, and
`/artifacts/<job_id>/native_report_archive`. The final PDF includes links to
those same artifacts. In the API response, check `report_result.file_path`
for the PDF location and `execution_artifacts.artifacts` for the native report
references. The tool-specific roots can be changed with
`K6_EXECUTION_ARTIFACTS_ROOT` and `JMETER_EXECUTION_ARTIFACTS_ROOT`. Avoid the
legacy shared `EXECUTION_ARTIFACTS_ROOT` setting when separate tool folders
are required.

For example, after confirming that `reqres.in` is approved for your test,
configure:

```dotenv
REAL_EXECUTION_ENABLED=true
REAL_EXECUTION_EXTERNAL_TARGETS_ENABLED=true
REAL_EXECUTION_ALLOWED_HOSTS=localhost,127.0.0.1,reqres.in
REAL_EXECUTION_ALLOWED_PORTS=8000,443
```

Then define the catalog case with `environment: "external_api"`,
`target_url: "https://reqres.in"`, and `endpoint: "/api/users/2"`. Keep
`target_url` as the origin; the request path belongs in `endpoint`. Include the
method, expected status, p95 threshold, users, max RPS, duration, ramp-up, and
`credentials_ref: "none"` for an unauthenticated endpoint. For a protected
API, use `header_env` to map header names to environment variable names, for
example `{"x-api-key": "REQRES_API_KEY"}`; set the secret value in the
process environment or `.env`, never in the catalog. The runner forwards only
the explicitly referenced variables to k6. The external path uses the same
reviewed k6 template and native-report artifact flow and does not require the
local mock server.

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
SCRIPT_PATH="src/generated_scripts/k6 native reports/$JOB_ID/k6_PTC_011_Local_Mock_Payment_API_k6_Script_Generation.js"
k6 inspect -e BASE_URL=http://localhost:8000 "$SCRIPT_PATH"
k6 run -e BASE_URL=http://127.0.0.1:8000 "$SCRIPT_PATH"
```

Replace the example `JOB_ID` with the prepared run's job ID.

Each request receives a generated `JOB-<uuid>` and a planned directory under
`src/generated_scripts/k6 native reports/<job_id>/`. Phase 1 defines the job status
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
time series, runner logs, and the native HTML dashboard in the per-job
directory under `src/generated_scripts/k6 native reports/<job_id>/`. The
artifact manifest and final PDF link directly to those job-local files.
A k6 threshold breach is a completed run with failing metrics; tool,
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

### Automatic passive security assessment of external APIs

Every REAL run against an external HTTPS API is assessed by the security agent
without being asked, after the performance run has ended. The assessment is
passive and non-intrusive: it never sends an attack payload, a request body, or
a state-changing request, and it needs no LLM call. It is not a penetration
test. Attack-style testing of services you do not own is deliberately not part
of it.

**What runs.** One TLS handshake with certificate verification on, plus at most
five ordinary `HEAD`/`GET`/`OPTIONS` requests to the job's own target (the
catalog test case's `target_url` and `endpoint`), and, from the performance
run's own results, the status-code distribution. If the declared method is
`POST`/`PUT`/`PATCH`/`DELETE`, that method is never sent; `OPTIONS` is used
instead and header checks that would need a normal response are inconclusive.

| Check id | What it looks at |
|---|---|
| `tls_protocol`, `tls_certificate` | negotiated TLS version and cipher; chain, hostname and expiry |
| `https_redirect` | plain HTTP on port 80 redirects to HTTPS (or is closed) |
| `header_hsts`, `header_x_content_type_options`, `header_frame_protection`, `header_csp`, `header_referrer_policy`, `header_permissions_policy`, `header_cache_control` | response security headers and their values |
| `header_information_disclosure`, `header_cookie_attributes` | `Server`/`X-Powered-By` version leaks; Secure/HttpOnly/SameSite (only when a cookie is set) |
| `cors_foreign_origin` | CORS preflight sent with a reserved foreign origin |
| `http_methods_exposed` | `Allow` header from `OPTIONS` (TRACE, CONNECT, WebDAV) |
| `error_leakage` | stack traces, database errors, debug pages or server paths in the error response for a missing resource |
| `rate_limit_evidence` | HTTP 429 in the run's own traffic, or rate-limit headers (positive evidence only) |

**One verdict per check.** Each check is `passed`, `failed` or `inconclusive`,
with its severity, a one-line reason, the evidence and, for a failure, a
recommendation. The overall status (`PASS`, `WARNING`, `FAIL`) and the score are
computed only from the assessed (passed or failed) checks: a failed
high/critical check gives `FAIL`, a failed medium/low check gives `WARNING`, and
informational checks never change the status. An `inconclusive` check is never
counted as a pass or a failure. An HTTP 401, 403, 404, 405, 429 or 5xx on the
resource itself never counts as a pass, and missing headers on such a response
are never counted as a failure. `assessment_outcome` says whether everything was
assessed, only some checks were (`partially_assessed`), or none were.

**Scope rules (independent of the load-test allowlist).** A target is accepted
when it is a public HTTPS host with no credentials in the URL, a DNS name (not an
IP literal), port 443 only, and every address it resolves to is globally
routable (loopback, private, link-local, carrier-grade NAT and cloud-metadata
addresses are refused). Connections go to the addresses verified once, so a
changing DNS answer cannot redirect a probe. If `environment` is missing from the
profile it is inferred as `external_api`. Port 80 is contacted only for the
redirect check.

**Reading the results.** Findings describe the externally visible edge, which
may be a CDN or WAF in front of the application. On a network that inspects TLS,
the certificate seen is the proxy's; compare the issuer in the evidence.

**Switches.**

- `SECURITY_AUTO_ASSESSMENT_ENABLED` (default `true`): assess REAL runs against
  external APIs automatically. Set `false` to run security only when asked.
- `SECURITY_PASSIVE_ASSESSMENT_ENABLED` (default `true`): master switch for every
  passive request, including those of an explicit security request. When `false`,
  explicit requests fall back to the older single `HEAD` observation, which still
  needs `SECURITY_LIVE_TESTS_ENABLED=true`.
- Per run, write "skip security" or "do not run security" in the request or Jira
  text. Security wording ("assess the security surface") runs the full security
  agent as before, now with the same passive checks plus any configuration
  controls requested; "configuration-only" sends nothing.

The automatic path is model-free and deterministic. Its result is stored as the
job's `security_result`, carried through Analysis with every per-check verdict
intact, and printed in the PDF under "Security Findings (Security Agent)".

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
PDF are in `src/generated_scripts/k6 native reports/<job_id>/`.

For a generation-only check, select PTC-011 and ask:

> Generate the k6 script for test case PTC-011 only. Do not run the test.

For execution and reporting, select PTC-012 as above. It is intentionally
capped at one virtual user, 5 RPS, and 40 seconds against the local mock.
Wait for the test-execution, monitoring, analysis, and report agents to
finish. Review the final response and open the consolidated PDF from the
ADK artifact panel or the job artifact directory. PDF artifact links require
the configured artifact bearer token when opened outside ADK; see the
artifact-access settings above.
