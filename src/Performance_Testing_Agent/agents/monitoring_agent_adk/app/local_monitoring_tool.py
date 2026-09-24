"""
Temporary, non-MCP implementation of the Monitoring tool.
 
This exists only because the McpToolset connection to server.py has been
failing with "Connection closed" during the MCP initialize handshake --
a transport-level failure in the mcp/anyio stdio-subprocess plumbing on
this machine, not a bug in server.py's own logic. server.py is NOT
modified and NOT deleted; its CSV-reading and analysis logic is simply
duplicated here, called directly instead of through a subprocess.
 
Once the MCP connection issue is resolved (package upgrade, a different
transport, etc.), switch monitoring_worker_agent's tools=[] back to
[monitoring_mcp] in agent.py and this file becomes unnecessary again.
"""
 
import csv
from pathlib import Path
 
BASE_DIR = Path(__file__).resolve().parent
MONITORING_FILE = BASE_DIR / "data" / "monitoring.csv"
 
 
def _read_monitoring_data():
    if not MONITORING_FILE.exists():
        return []
    try:
        with open(MONITORING_FILE, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            return list(reader)
    except Exception:
        return []
 
 
def _get_value(row, *names):
    for name in names:
        if name in row:
            try:
                return float(row[name])
            except (ValueError, TypeError):
                pass
    return None
 
 
def collect_monitoring_metrics() -> dict:
    """
    Reads monitoring.csv directly (no MCP/subprocess involved) and
    returns the same averaged CPU/memory/DB connections/response time/
    TPS metrics and alerts that the Monitoring MCP server computes.
    """
    rows = _read_monitoring_data()
 
    if not rows:
        return {
            "status": "FAILED",
            "tool": "Monitoring",
            "error": "No monitoring data was found.",
        }
 
    cpu_values, memory_values, db_values = [], [], []
    response_values, tps_values = [], []
 
    for row in rows:
        v = _get_value(row, "CPU (%)", "cpu_percent", "CPU", "CPU Usage")
        if v is not None:
            cpu_values.append(v)
        v = _get_value(row, "Memory (%)", "memory_percent", "Memory", "Memory Usage")
        if v is not None:
            memory_values.append(v)
        v = _get_value(row, "DB Connections", "db_connections", "Database Connections")
        if v is not None:
            db_values.append(v)
        v = _get_value(row, "Response Time (ms)", "response_time_ms", "Response Time")
        if v is not None:
            response_values.append(v)
        v = _get_value(row, "TPS", "tps", "Transactions Per Second")
        if v is not None:
            tps_values.append(v)
 
    def _avg(values):
        return round(sum(values) / len(values), 2) if values else None
 
    cpu = _avg(cpu_values)
    memory = _avg(memory_values)
    db_connections = _avg(db_values)
    response_time = _avg(response_values)
    tps = _avg(tps_values)
 
    alerts = []
    if cpu is not None and cpu > 85:
        alerts.append("High CPU Usage")
    if memory is not None and memory > 80:
        alerts.append("High Memory Usage")
    if response_time is not None and response_time > 1000:
        alerts.append("High Response Time")
 
    return {
        "status": "COMPLETED",
        "tool": "Monitoring",
        "records_analyzed": len(rows),
        "cpu_usage": cpu,
        "memory_usage": memory,
        "db_connections": db_connections,
        "response_time_ms": response_time,
        "tps": tps,
        "alerts": alerts,
        "message": "Monitoring analysis completed using the provided monitoring data.",
    }