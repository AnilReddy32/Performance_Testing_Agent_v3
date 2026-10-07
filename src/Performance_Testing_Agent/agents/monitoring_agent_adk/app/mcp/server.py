import csv

from pathlib import Path
 
from mcp.server.fastmcp import FastMCP

from datetime import datetime, timezone
 
 
mcp = FastMCP("Monitoring Performance Server")
 
 
# ---------------------------------------------------------

# Project paths

# ---------------------------------------------------------
 
BASE_DIR = Path(__file__).resolve().parents[1]
 
MONITORING_FILE = (

    BASE_DIR

    / "data"

    / "monitoring.csv"

)
 
RESULT_DIR = (

    BASE_DIR

    / "data"

    / "performance_results"

    / "monitoring"

)
 
RESULT_DIR.mkdir(

    parents=True,

    exist_ok=True

)
 
 
# ---------------------------------------------------------

# Read monitoring data

# ---------------------------------------------------------
 
def read_monitoring_data():
 
    if not MONITORING_FILE.exists():
 
        return []
 
    try:
 
        with open(

            MONITORING_FILE,

            "r",

            encoding="utf-8-sig",

            newline=""

        ) as file:
 
            reader = csv.DictReader(file)
 
            return list(reader)
 
    except Exception:
 
        return []
 
 
# ---------------------------------------------------------

# Check monitoring

# ---------------------------------------------------------
print("===== CHECK_MONITORING CALLED =====")
@mcp.tool()


def check_monitoring(
    job_id: str = "",
    application: str = "",
    scenario: str = ""
) -> dict:

    """

    Check whether monitoring data is available.

    """
 
    if not MONITORING_FILE.exists():
 
        return {

            "status": "UNAVAILABLE",

            "tool": "Monitoring",

            "error": (

                f"Monitoring file not found: "

                f"{MONITORING_FILE}"

            )

        }
 
    return {

        "status": "AVAILABLE",

        "tool": "Monitoring",

        "data_source": str(MONITORING_FILE),

        "execution_mode": "MOCK"

    }
 
 
# ---------------------------------------------------------

# Get monitoring metrics

# ---------------------------------------------------------
print("===== GET_MONITORING_METRICS CALLED =====")
@mcp.tool()
def get_monitoring_metrics(
    job_id: str = "",
    application: str = "",
    scenario: str = ""
) -> dict:

    """

    Analyze the existing monitoring.csv file.

    """

    # Auto-generate a job_id/scenario when this was called standalone (no
    # Test Execution context to inherit job_id/scenario from) - done here
    # in code, deterministically, rather than left to the LLM to invent a
    # timestamp itself.
    if not job_id:

        job_id = f"MON-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    if not scenario:

        scenario = "Standalone Monitoring Check"
 
    rows = read_monitoring_data()
 
    if not rows:
 
        return {

            "status": "FAILED",

            "tool": "Monitoring",

            "error": (

                "No monitoring data was found."

            )

        }
 
    # ---------------------------------------------

    # Support multiple possible column names

    # ---------------------------------------------
 
    def get_value(

        row,

        *names

    ):
 
        for name in names:
 
            if name in row:
 
                try:
 
                    return float(

                        row[name]

                    )
 
                except (

                    ValueError,

                    TypeError

                ):
 
                    pass
 
        return None
 
    cpu_values = []

    memory_values = []

    db_values = []

    response_values = []

    tps_values = []
 
    for row in rows:
 
        value = get_value(

            row,

            "CPU (%)",

            "cpu_percent",

            "CPU",

            "CPU Usage"

        )
 
        if value is not None:

            cpu_values.append(value)
 
        value = get_value(

            row,

            "Memory (%)",

            "memory_percent",

            "Memory",

            "Memory Usage"

        )
 
        if value is not None:

            memory_values.append(value)
 
        value = get_value(

            row,

            "DB Connections",

            "db_connections",

            "Database Connections"

        )
 
        if value is not None:

            db_values.append(value)
 
        value = get_value(

            row,

            "Response Time (ms)",

            "response_time_ms",

            "Response Time"

        )
 
        if value is not None:

            response_values.append(value)
 
        value = get_value(

            row,

            "TPS",

            "tps",

            "Transactions Per Second"

        )
 
        if value is not None:

            tps_values.append(value)
 
    # ---------------------------------------------

    # Calculate averages

    # ---------------------------------------------
 
    def average(values):
 
        if not values:

            return None
 
        return round(

            sum(values) / len(values),

            2

        )
 
    cpu = average(cpu_values)
 
    memory = average(memory_values)
 
    db_connections = average(

        db_values

    )
 
    response_time = average(

        response_values

    )
 
    tps = average(

        tps_values

    )
 
    # ---------------------------------------------

    # Alerts

    # ---------------------------------------------
 
    alerts = []
 
    if cpu is not None and cpu > 85:
 
        alerts.append(

            "High CPU Usage"

        )
 
    if memory is not None and memory > 80:
 
        alerts.append(

            "High Memory Usage"

        )
 
    if (

        response_time is not None

        and response_time > 1000

    ):
 
        alerts.append(

            "High Response Time"

        )
 
    # ---------------------------------------------

    # Result

    # ---------------------------------------------
 
    result = {

        "job_id": job_id,

        "application": application or "unknown",

        "scenario": scenario,
 
        "status": "COMPLETED",
 
        "tool": "Monitoring",
 
        "execution_mode": "MOCK",
 
        "data_source":

            str(MONITORING_FILE),
 
        "records_analyzed":

            len(rows),
 
        "cpu_usage":

            cpu,
 
        "memory_usage":

            memory,
 
        "db_connections":

            db_connections,
 
        "response_time_ms":

            response_time,
 
        "tps":

            tps,
 
        "alerts":

            alerts,
 
        "message":

            (

                "Monitoring analysis completed "

                "using the provided monitoring data."

            )

    }
 
    # ---------------------------------------------

    # Save monitoring result

    # ---------------------------------------------
 
    result_file = (

        RESULT_DIR

        / "monitoring_summary.json"

    )
 
    import json
 
    result_file.write_text(

        json.dumps(

            result,

            indent=4

        ),

        encoding="utf-8"

    )
 
    result["result_file"] = str(

        result_file

    )
 
    return result
 
 
# ---------------------------------------------------------

# Start MCP

# ---------------------------------------------------------
 
if __name__ == "__main__":

    mcp.run()