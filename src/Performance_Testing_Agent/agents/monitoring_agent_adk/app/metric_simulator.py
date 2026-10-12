"""
Simulated infrastructure metrics for the Monitoring Agent.

WHY THIS EXISTS
---------------
monitoring_agent previously needed CPU/Memory/DB Connections/Response Time/
TPS numbers to already exist somewhere (a Jira ticket, a CSV file) before it
could report anything. That depends on a person typing or supplying
realistic-looking numbers -- but a real user asking "please monitor this
test" has no way of knowing what the CPU or memory will actually be; those
are things that get measured while the test runs, not something anyone can
predict ahead of time and type in.

This module replaces that with a small, local calculation that runs fresh
every time monitoring_agent is called, taking that SAME run's real
test_execution_result (already sitting in shared session state -- see
test_execution_agent's own tool_context.state["test_execution_result"]
write) and using it to calculate plausible CPU/Memory/DB Connections/TPS/
Response Time numbers for that run: a slow, failing test produces strained
infrastructure numbers; a clean, fast test produces healthy ones.

Nothing here is read from a file and nothing is hand-typed -- every number
is calculated on the spot. There is no real monitoring tool (Dynatrace,
AppDynamics, Prometheus, CloudWatch, etc.) behind this yet; this is clearly
labelled "simulated" in its own output (see data_source below) so nobody
mistakes it for a real production reading later. The moment a real
monitoring tool IS connected, only this one file needs to change -- nothing
about monitoring_agent's instruction, analysis_agent, or report_agent needs
to change, since they already just read whatever ends up in
session.state["monitoring_result"].

REPRODUCIBLE, NOT RANDOM
-------------------------
The numbers vary realistically from ticket to ticket, but are NOT a dice
roll on every run: they're seeded from that run's own job_id, so re-running
the exact same test result always produces the exact same simulated
reading. That makes it possible to predict and verify exactly what
monitoring should report for a given test, and to check that analysis_agent
and report_agent handled it correctly -- important while you're still
testing/validating the agents themselves, separately from how closely the
numbers resemble a real system (there is no real system yet to compare
against).

TWO MODES
---------
1. A real test_execution_result for this run is available in session state
   (the normal case: the ticket asked for a performance test) -- numbers
   are derived from that run's own error rate and response time.
2. No test_execution_result is available (a "monitoring only" ticket, with
   no test requested) -- there's nothing to derive numbers from, so this
   falls back to a realistic steady-state/baseline reading instead,
   representing "here's the API's current health right now", independent
   of any specific test.
"""

import hashlib
import random


def _seeded_rng(seed_key: str) -> random.Random:
    """A random generator seeded from seed_key -- same key always produces
    the same sequence, different keys produce different sequences. This is
    what makes the simulated numbers reproducible per ticket instead of
    genuinely random."""
    seed = int(hashlib.sha256(seed_key.encode("utf-8")).hexdigest(), 16) % (2**32)
    return random.Random(seed)


def _status_and_alerts(cpu: float, memory: float, response_time: float) -> tuple[str, list]:
    alerts = []
    if cpu > 85:
        alerts.append("High CPU Usage")
    if memory > 80:
        alerts.append("High Memory Usage")
    if response_time > 1000:
        alerts.append("High Response Time")

    if cpu > 95 or memory > 95:
        status = "CRITICAL"
    elif alerts:
        status = "WARNING"
    else:
        status = "OK"

    return status, alerts


def _simulate_from_test_execution(test_execution_result: dict) -> dict:
    """Derives CPU/Memory/DB Connections/TPS/Response Time from this run's
    OWN real test_execution_result -- a slow/failing test produces strained
    infra numbers, a clean/fast test produces healthy ones."""

    job_id = test_execution_result.get("job_id", "unknown_job")
    rng = _seeded_rng(f"monitoring::{job_id}")

    # error_rate is already guaranteed to be a 0-100 percentage by
    # test_execution_agent's own validation (see result_formatter.py /
    # handoff.py's validate_analysis_payload()).
    error_rate = test_execution_result.get("error_rate", 0) or 0
    avg_response_time = test_execution_result.get("avg_response_time", 0) or 0
    throughput = test_execution_result.get("throughput", 0) or 0

    # 0 (healthy) .. 1 (saturated) "how strained is this run" signal, from
    # whichever of error rate / response time looks worse.
    error_strain = min(error_rate / 5.0, 1.0)
    latency_strain = min(avg_response_time / 2000.0, 1.0)
    strain = max(error_strain, latency_strain)

    cpu = round(35 + strain * 60 + rng.uniform(-4, 4), 1)
    memory = round(40 + strain * 50 + rng.uniform(-4, 4), 1)
    db_connections = round(60 + strain * 150 + rng.uniform(-10, 10), 1)
    response_time = round(avg_response_time * (1.05 + strain * 0.15), 1) if avg_response_time else round(150 + strain * 400, 1)
    tps = round(max(throughput * rng.uniform(0.85, 0.95), 1.0), 1) if throughput else round(max(20 - strain * 15, 1), 1)

    cpu = max(0.0, min(cpu, 100.0))
    memory = max(0.0, min(memory, 100.0))

    status, alerts = _status_and_alerts(cpu, memory, response_time)

    return {
        "cpu_usage": cpu,
        "memory_usage": memory,
        "db_connections": db_connections,
        "response_time": response_time,
        "tps": tps,
        "status": status,
        "alerts": alerts,
        "data_source": "simulated (derived from this run's test_execution results)",
    }


def _simulate_baseline(seed_key: str) -> dict:
    """No test_execution_result was available this run (a "monitoring
    only" request) -- there's nothing to derive numbers from, so this
    returns a realistic steady-state baseline reading instead."""

    rng = _seeded_rng(f"monitoring_baseline::{seed_key}")

    cpu = round(30 + rng.uniform(0, 20), 1)
    memory = round(35 + rng.uniform(0, 20), 1)
    db_connections = round(40 + rng.uniform(0, 30), 1)
    response_time = round(150 + rng.uniform(0, 100), 1)
    tps = round(20 + rng.uniform(0, 15), 1)

    status, alerts = _status_and_alerts(cpu, memory, response_time)

    return {
        "cpu_usage": cpu,
        "memory_usage": memory,
        "db_connections": db_connections,
        "response_time": response_time,
        "tps": tps,
        "status": status,
        "alerts": alerts,
        "data_source": "simulated (baseline -- no test_execution result was available this run)",
    }


def simulate_monitoring_metrics(test_execution_result: dict | None) -> dict:
    """Entry point used by monitoring_agent's tool. Picks whichever of the
    two modes above applies, and always returns the same shape, regardless
    of which mode was used."""

    job_id = (test_execution_result or {}).get("job_id", "unknown_job")
    application = (test_execution_result or {}).get("application", "unknown")
    scenario = (test_execution_result or {}).get("scenario", "unknown")

    has_real_test_data = bool(test_execution_result) and {
        "error_rate", "avg_response_time", "throughput",
    }.issubset(test_execution_result.keys())

    if has_real_test_data:
        metrics = _simulate_from_test_execution(test_execution_result)
    else:
        metrics = _simulate_baseline(job_id if job_id != "unknown_job" else "no_job_id")

    return {
        "job_id": job_id,
        "application": application,
        "scenario": scenario,
        **metrics,
    }
