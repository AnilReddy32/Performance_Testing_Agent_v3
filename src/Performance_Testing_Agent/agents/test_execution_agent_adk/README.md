# Test Execution Agent

An agentic performance-testing component built with **Google ADK**. The agent accepts natural-language performance-testing requests, converts them into a structured plan, selects the appropriate capability, generates testing artifacts, executes the requested workflow, monitors execution, standardizes the results, and prepares a payload for the Analysis Agent.

Supported performance-testing tools:
- **k6**
- **Apache JMeter**
- **Gatling**
- **It also supports synthetic test-data generation and test-environment preparation**.

---

## 1. Project Objective

The goal of this project is to provide a **Test Execution Agent** that understands requests such as:

> Run a load test using k6 for the Payments API with 100 virtual users for 60 seconds.

> Generate 100,000 banking transactions.

> Create a JMeter script for the Login service.

The agent uses an LLM-based planner to extract the important parameters from natural language rather than requiring a rigid command format.

The Test Execution Agent is responsible for the execution side of the performance-testing workflow.

The **Analysis Agent is a separate component**. After an execution request completes, this agent prepares a standardized result containing the metrics required by the Analysis Agent.

---

## 2. High-Level Architecture

```text
                         User Request
                              |
                              v
                    +--------------------+
                    |   Test Execution   |
                    |       Agent        |
                    +--------------------+
                              |
                              v
                    +--------------------+
                    |   Test Planner     |
                    |  Natural Language  |
                    |    -> JSON Plan    |
                    +--------------------+
                              |
                              v
                    +--------------------+
                    |  Tool Dispatcher   |
                    +--------------------+
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
      Generate Script   Generate Data   Prepare Environment
             |                |                |
             +----------------+----------------+
                              |
                              v
                    +--------------------+
                    |    Execute Test     |
                    |   k6 / JMeter /    |
                    |      Gatling       |
                    +--------------------+
                              |
                              v
                    +--------------------+
                    |       MCP /        |
                    |  Execution Service |
                    +--------------------+
                              |
                              v
                    +--------------------+
                    |     Monitoring     |
                    +--------------------+
                              |
                              v
                    +--------------------+
                    |  Result Formatter  |
                    +--------------------+
                              |
                              v
                    +--------------------+
                    |  Analysis Agent    |
                    |      Handoff       |
                    +--------------------+
```

---

## 3. Current Execution Architecture

The current design uses the same execution path for k6, JMeter, and Gatling.

```text
k6       JMeter    ---> execution.py ---> MCP ---> monitoring.py
Gatling  /                         |
                                  v
                           result_formatter.py
                                  |
                                  v
                         Analysis Agent Handoff
```

The generated script remains tool-specific, but execution, monitoring, result formatting, and handoff are shared.

---

## 4. Project Structure

```text
test_execution_agent_adk/
│
├── app/
│   ├── __init__.py
│   ├── agent.py
│   │
│   ├── tools/
│   │   ├── test_planner.py
│   │   ├── tool_dispatcher.py
│   │   ├── tool_executor.py
│   │   ├── artifact_generator.py
│   │   ├── script_generation.py
│   │   ├── data_generation.py
│   │   ├── environment.py
│   │   ├── execution.py
│   │   ├── monitoring.py
│   │   ├── result_formatter.py
│   │   └── ...
│   │
│   ├── mcp/
│   │   └── ...
│   │
│   └── analysis_agent/
│       └── handoff.py
│
├── generated_scripts/
│   └── ...
│
├── generated_data/
│   └── ...
│
├── mock_api/
│   └── app.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

Generated artifacts and secrets should not be committed to GitHub.

---

# 5. File Responsibilities

## `app/agent.py`

Main Google ADK agent entry point.

Responsible for exposing the Test Execution Agent through ADK and connecting the agent to the project's tools/workflows.

---

## `app/tools/test_planner.py`

Converts a natural-language performance-testing request into a structured JSON plan using the OpenAI API.

The planner extracts:

```json
{
  "intent": "",
  "test_type": "",
  "tool": "",
  "application": "",
  "scenario": "",
  "api_name": "",
  "users": 0,
  "duration": 0
}
```

Supported intents:

```text
execute_test
generate_script
generate_test_data
prepare_environment
invalid
```

Example:

```text
Run a load test using k6 for the Payments API
with 100 virtual users for 60 seconds.
```

becomes a structured plan containing values such as:

```text
intent      -> execute_test
test_type   -> load
tool        -> k6
application -> Payments
api_name    -> Payments API
users       -> 100
duration    -> 60
```

The planner does not execute tests or fabricate performance metrics.

---

## `app/tools/tool_dispatcher.py`

Determines which capability should handle the planner's output.

Mapping:

```text
execute_test
    -> run_execution_workflow

generate_script
    -> generate_script

generate_test_data
    -> generate_test_data

prepare_environment
    -> prepare_environment
```

Invalid or unsupported requests are stopped rather than sent to an unrelated capability.

---

## `app/tools/tool_executor.py`

The execution layer between the planner/dispatcher and the actual capabilities.

Responsibilities:

1. Create the planner.
2. Send the user request to the planner.
3. Validate the planning result.
4. Dispatch the selected capability.
5. Call the appropriate implementation.

Example entry point:

```python
from app.tools.tool_executor import handle_test_request

result = handle_test_request(
    "Run a load test using k6 for the Payments API with 10 virtual users for 10 seconds."
)
```

---

## `app/tools/artifact_generator.py`

Contains the LLM-driven artifact-generation logic for performance-testing scripts.

Supports:

```text
k6
JMeter
Gatling
```

The generator produces tool-specific artifacts while applying validation rules appropriate to each tool.

For k6, generated scripts use configurable environment variables such as:

```text
BASE_URL
API_PATH
VUS
DURATION
EXPECTED_STATUS
```

Generated k6 scripts also generate unique transaction identifiers when repeated transactions require them.

---

## `app/tools/script_generation.py`

Provides the higher-level script-generation capability used by the workflow.

Generated scripts are stored under:

```text
generated_scripts/
```

Examples:

```text
k6_Payments_API.js
k6_Account_Balance_API.js
JMeter_Login_Service.jmx
Gatling_Fund_Transfer.scala
```

---

## `app/tools/data_generation.py`

Generates synthetic test data required by performance-testing workflows.

Examples:

- Banking transactions
- Customer data
- Test accounts
- Login credentials
- Dynamic transaction data

For `generate_test_data` requests, the planner uses the `users` field to represent the requested record count.

Example:

```text
Generate 100,000 banking transactions
```

becomes:

```text
intent = generate_test_data
users = 100000
```

Generated data is stored under:

```text
generated_data/
```

Data generation is independent of performance-test execution.

---

## `app/tools/environment.py`

Prepares the test environment metadata required by the workflow.

It receives information such as:

```text
application
scenario
environment
users
requirements
```

and returns an environment result/identifier.

---

## `app/tools/execution.py`

Starts performance-test execution through the project's MCP execution service.

It accepts parameters such as:

```text
tool
test_type
users
duration
ramp_up
target
application
scenario
api_name
additional_parameters
```

The same execution function is used for:

```text
k6
JMeter
Gatling
```

---

## `app/tools/monitoring.py`

Monitors an execution started by `execution.py`.

It uses the execution ID returned by the MCP execution service, waits for completion, and retrieves the execution result/metrics.

Flow:

```text
Execution
   |
   v
execution_id
   |
   v
Monitoring
   |
   v
Completed execution + metrics
```

---

## `app/tools/result_formatter.py`

Converts execution and monitoring information into the standardized performance-test result used by the Analysis Agent.

The result contains exactly 13 fields:

```text
job_id
application
scenario
api_name
total_requests
successful_requests
failed_requests
avg_response_time
p95_response_time
max_response_time
throughput
error_rate
http_status
```

---

## `app/analysis_agent/handoff.py`

Prepares the standardized execution result for the separate Analysis Agent.

The Test Execution Agent does not perform the analysis itself.

The handoff contract is:

```json
{
  "job_id": "...",
  "application": "...",
  "scenario": "...",
  "api_name": "...",
  "total_requests": 0,
  "successful_requests": 0,
  "failed_requests": 0,
  "avg_response_time": 0.0,
  "p95_response_time": 0.0,
  "max_response_time": 0.0,
  "throughput": 0.0,
  "error_rate": 0.0,
  "http_status": 200
}
```

---

## `app/mcp/`

Contains the MCP-related execution layer.

The current project uses MCP/simulation infrastructure for the common execution path.

It represents operations such as:

```text
Start execution
Monitor execution
Retrieve execution results
```

The current implementation is a development/simulation layer; the standardized results should not be interpreted as measurements from a production load test.

---

## `mock_api/app.py`

Provides a local Flask API that can be used as a development/test target.

Current endpoints include:

```text
POST /api/v1/payment
POST /api/v1/payment/failure
GET  /health
```

The payment endpoint accepts test payment information and returns a simulated payment response.

This mock API is useful for independently validating generated k6 scripts.

---

## `generated_scripts/`

Stores generated performance-testing artifacts.

Examples:

```text
k6_Payments_API.js
k6_Account_Balance_API.js
k6_NEFT_performance_API.js
```

These are generated outputs and should normally be excluded from version control.

---

## `generated_data/`

Stores synthetic test-data artifacts.

Examples:

```text
transactions.csv
customer_data.csv
test_accounts.csv
login_credentials.csv
```

These are generated outputs and should normally be excluded from version control.

---

## `requirements.txt`

Contains the Python dependencies required by the project, including:

```text
google-adk
litellm
python-dotenv
openai
```

---

# 6. Complete Project Flow

## A. Execute Performance Test

Example:

```text
Run a stress test using k6 for the Payments API
with 100 virtual users for 60 seconds.
```

Flow:

```text
User Request
     |
     v
Test Planner
     |
     v
Structured Plan
     |
     v
Tool Dispatcher
     |
     v
run_execution_workflow
     |
     +----> Generate Script
     |
     +----> Generate Test Data
     |
     +----> Prepare Environment
     |
     +----> Execute Test
                 |
                 v
              MCP
                 |
                 v
             Monitoring
                 |
                 v
          Result Formatter
                 |
                 v
        Analysis Agent Handoff
```

---

## B. Generate Script

Example:

```text
Create a k6 script for the UPI Payment API.
```

Flow:

```text
User
 |
 v
Planner
 |
 v
intent = generate_script
 |
 v
Dispatcher
 |
 v
generate_script()
 |
 v
Artifact Generator
 |
 v
k6/JMeter/Gatling script
 |
 v
generated_scripts/
```

No performance test is executed and no execution metrics are generated.

---

## C. Generate Test Data

Example:

```text
Generate 100,000 banking transactions.
```

Flow:

```text
User
 |
 v
Planner
 |
 v
intent = generate_test_data
users = 100000
 |
 v
Dispatcher
 |
 v
generate_test_data()
 |
 v
CSV/JSON artifact
 |
 v
generated_data/
```

This is an artifact-generation request, not a performance-test execution request.

---

## D. Prepare Environment

Example:

```text
Prepare the test environment for 500 concurrent banking users.
```

Flow:

```text
User
 |
 v
Planner
 |
 v
intent = prepare_environment
 |
 v
Dispatcher
 |
 v
prepare_environment()
 |
 v
Environment Result
```

---

# 7. Standardized Analysis Agent Contract

Every completed performance-test execution produces the standardized Analysis Agent contract:

```text
job_id
application
scenario
api_name
total_requests
successful_requests
failed_requests
avg_response_time
p95_response_time
max_response_time
throughput
error_rate
http_status
```

Validation invariants:

```text
successful_requests + failed_requests = total_requests

0 <= error_rate <= 100

p95_response_time >= avg_response_time

max_response_time >= p95_response_time
```

This keeps the interface between the Test Execution Agent and Analysis Agent predictable.

---

# 8. Supported Performance-Testing Scenarios

The agent is designed to understand:

- Load testing
- Stress testing
- Endurance testing
- Spike testing
- Concurrent-user testing
- General performance testing

Domain examples include:

- UPI payments
- Payment gateways
- Account balance APIs
- Login services
- Fund transfers
- NEFT
- IMPS
- RTGS
- Branch banking transactions
- Bulk transactions
- Internet banking
- Synthetic banking data

---

# 9. Example Requests

### Execute a load test

```text
Run a load test using k6 for the Payments API with 100 virtual users for 60 seconds.
```

### Execute a stress test

```text
Run a stress test using JMeter for the Login service with 500 users for 5 minutes.
```

### Generate a script

```text
Create a Gatling script for Fund Transfer APIs.
```

### Generate test data

```text
Generate 100,000 banking transactions.
```

### Generate credentials

```text
Generate 10,000 login credentials for virtual users.
```

### Prepare environment

```text
Prepare the test environment for 1,000 concurrent users for Internet Banking.
```

```text
Test Group 1 – Script Generation
Generate a JMeter script for the Login API.
Generate a k6 script for the UPI Payment API.
Generate a Gatling script for Fund Transfer APIs.

Test Group 2 – Data Generation
Generate 100000 banking transactions.
Prepare synthetic banking customer test data.
Generate login credentials for virtual users.

Test Group 3 – Execution
Execute a load test for Internet Banking Login API with 100 virtual users.
Execute a load test for Internet Banking UPI Payment API with 500 virtual users.
Execute payment gateway performance testing.
Run API load testing for Account Balance APIs.
Execute branch banking transaction testing.
Execute concurrent user simulation.

Test Group 4 – Planner Intelligence
Execute UPI Payment load test for Internet Banking.
Execute NEFT transaction performance testing.
Run IMPS transaction performance testing.
Execute RTGS transaction load testing.

Test Group 5 – End-to-End Flow
Execute a stress test until the application breaks.
Run an endurance test for 12 hours.
Execute a spike test with sudden traffic increase.
Execute performance testing for NEFT transactions with 5000 virtual users.

Generate a k6 performance testing script for the UPI Payment API in Internet Banking.
Create a JMeter performance testing script for the Login service in Internet Banking.
Generate a Gatling performance testing script for the Fund Transfer APIs in Internet Banking.
Generate 1000 synthetic banking customer records for performance testing.
Generate 100,000 synthetic banking transactions for performance testing.
Execute a stress test using k6 for the NEFT performance API with 2000 virtual users for 120 seconds.
TC7 — Default execution parameters: Execute a performance test for the Account Balance API in Internet Banking.
TC8 — Load test with large user count: Execute a load test for the Payment Gateway API with 5000 virtual users for 60 seconds.
TC9 — Endurance test: Execute an endurance test for the Internet Banking Login service with 100 virtual users for 12 hours.
TC10 — Spike test: Execute a spike test for the UPI Payment API with 1000 virtual users for 30 seconds.
TC11 — Concurrent user simulation: Simulate 500 concurrent users accessing the Internet Banking Account Balance API for 120 seconds.
TC12 — Explicit Gatling execution: Execute a load test using Gatling for the Fund Transfer API with 200 virtual users for 60 seconds.
TC13 — Explicit JMeter execution: Execute a performance test using JMeter for the Login service with 100 virtual users for 60 seconds.
TC14 — Explicit k6 execution: Execute a load test using k6 for the Account Balance API with 300 virtual users for 90 seconds.
TC15 — Login credentials: Prepare 5000 login credentials for Internet Banking virtual users.
TC16 — Test account: Prepare 1000 test accounts for Internet Banking performance testing.
TC17 — NEFT transaction data: Generate 10000 synthetic NEFT transactions for performance testing.
TC18 — Different wording: I need to put 2500 concurrent users on the UPI payment endpoint for two minutes. Use k6.
TC19 — Duration conversion: Run a load test using 100 users against the Login API for 5 minutes.
TC20 — User-count conversion: Run a load test for 2K virtual users against the Payment API for 2 minutes.
TC21 — Completely unrelated request: What is the capital of France?
TC22 — Non-performance programming request: Write a Python program to sort a list of numbers.
TC24 — Explicit user count but no duration: Execute a load test for the UPI Payment API with 1000 virtual users.
TC25 — Explicit duration but no users: Execute a load test for the UPI Payment API for 5 minutes.
TC26 — Different banking scenario: Execute a load test for RTGS transactions with 1000 virtual users for 60 seconds.
TC27 — Another banking scenario: Execute a load test for IMPS transactions with 750 virtual users for 90 seconds.
```

---

# 10. Running the Project

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env`:

```text
OPENAI_API_KEY=your_openai_api_key
```

Never commit the actual `.env` file.

---

# 11. Testing the Agent Through Python

The complete planning and dispatch workflow can be tested with:

```python
from app.tools.tool_executor import handle_test_request

result = handle_test_request(
    "Run a load test using k6 for the Payments API with 10 virtual users for 10 seconds."
)

print(result)
```

To inspect the Analysis Agent handoff:

```python
import json

print(
    json.dumps(
        result.get("analysis_handoff"),
        indent=2
    )
)
```

For a synthetic-data request, the output is different because it is an artifact-generation workflow:

```python
result = handle_test_request(
    "Generate 100000 banking transactions."
)

print(result)
```

A data-generation request does not produce the 13-field execution-result contract because no performance test has been executed.

---

# 13. Future Extensions

Possible future extensions include:

- Real JMeter integration
- Real Gatling integration
- Real k6 execution through a controlled execution service
- Kubernetes-based load generators
- Vault-based test credentials
- Distributed load generation
- Advanced monitoring
- Richer Analysis Agent integration
- ADK-based multi-agent orchestration

These can be added after the current stable execution workflow.

---

# 14. Project Boundary

The **Test Execution Agent** is responsible for:

```text
Understand request
Generate artifacts
Generate test data
Prepare environment
Execute performance test
Monitor execution
Standardize results
Prepare Analysis Agent handoff
```

The **Analysis Agent** is responsible for consuming the standardized result and performing performance analysis.

This separation keeps execution and analysis independently maintainable.

---

# 15. Summary

The Test Execution Agent provides a natural-language interface for performance-testing workflows.

Core pipeline:

```text
Natural Language Request
          |
          v
      Test Planner
          |
          v
    Tool Dispatcher
          |
          v
   Tool / Capability
          |
          v
 Script + Data + Environment
          |
          v
       Execution
          |
          v
       Monitoring
          |
          v
    Result Formatting
          |
          v
 Analysis Agent Handoff
```

The architecture supports k6, JMeter, and Gatling while keeping execution and result handling consistent across tools.
