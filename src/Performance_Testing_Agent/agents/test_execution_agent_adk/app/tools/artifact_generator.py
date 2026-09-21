import os
import re
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class ArtifactGenerator:
    SUPPORTED_TOOLS = {"jmeter", "k6", "gatling"}

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def generate_script(
        self,
        tool,
        application,
        scenario,
        api_name,
    ):
        tool = tool.lower().strip()

        if tool not in self.SUPPORTED_TOOLS:
            return "UNSUPPORTED_TOOL"

        prompt = self._build_prompt(
            tool=tool,
            application=application,
            scenario=scenario,
            api_name=api_name,
        )

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior performance-testing engineer "
                        "who creates production-quality test artifacts. "
                        "Generate executable, configurable performance-test "
                        "scripts. Never invent undocumented production API "
                        "behavior, credentials, secrets, or response schemas. "
                        "Use explicit configuration placeholders when required "
                        "information is unavailable."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        if not response.choices:
            return "EMPTY_ARTIFACT"

        content = response.choices[0].message.content

        if not content:
            return "EMPTY_ARTIFACT"

        content = self._clean_response(content)

        if not content:
            return "EMPTY_ARTIFACT"

        if tool == "jmeter":
            if not self._validate_jmeter(content):
                return "INVALID_JMETER_ARTIFACT"

        elif tool == "k6":
            if not self._validate_k6(content):
                return "INVALID_K6_ARTIFACT"

        elif tool == "gatling":
            if not self._validate_gatling(content):
                return "INVALID_GATLING_ARTIFACT"

        return content

    @staticmethod
    def _build_prompt(
        tool,
        application,
        scenario,
        api_name,
    ):
        if tool == "k6":
            return f"""
Generate a production-quality k6 JavaScript performance-testing script.

TEST CONTEXT
------------
Application: {application}
Scenario: {scenario}
API/Service: {api_name}

IMPORTANT REQUIREMENTS
----------------------

1. Generate ONLY executable k6 JavaScript.
2. Do not use Markdown code fences.
3. Do not generate Python, Java, JavaScript server code,
   Flask, FastAPI, Node.js, JMeter, Gatling, or another framework.
4. Import k6/http and the required k6 modules correctly.

CONFIGURATION
-------------

The generated script must NOT contain a fake or invented external
production URL such as:

https://api.example.com
https://yourbank.com

Instead, use an environment variable:

const BASE_URL = __ENV.BASE_URL;

The script must fail clearly if BASE_URL is missing.

The endpoint path must NOT be invented as a real production API contract.

Always make the endpoint configurable through:

const API_PATH = __ENV.API_PATH || '/api/v1/payment';

The execution layer may override API_PATH through the environment.

If the exact endpoint path is unknown, treat the default above only
as a local/test configuration fallback. Do not claim that it is the
real production endpoint for the supplied API/service.

Never invent a production endpoint such as:
'/api/v1/accounts'
'/api/v1/fund-transfer'
'/api/v1/neft'
unless that endpoint was explicitly supplied by the user.

USER LOAD CONFIGURATION
-----------------------

Virtual users and duration must be configurable through environment
variables.

Use:

const VUS = Number(__ENV.VUS || 1);
const DURATION = __ENV.DURATION || '60s';

Configure them in:

export const options = {{
    vus: VUS,
    duration: DURATION,
}};

Do not hardcode arbitrary values such as 100 VUs and 30 seconds
as the only configuration.

REQUEST DATA
------------

Do not invent undocumented authentication, credentials, database data,
or API response schemas.

If the API request requires a body but the exact contract is not known,
create clearly identifiable configurable test data.

For example, environment variables may be used for values such as:

TEST_AMOUNT
TEST_UPI_ID
TEST_TRANSACTION_ID

Do not hardcode real credentials or secrets.

If transaction IDs are required for repeated performance requests,
generate unique test transaction identifiers rather than reusing
one constant transaction ID.

When generating unique transaction IDs using k6 execution-context
variables such as __VU or __ITER, these variables MUST only be
referenced inside the exported default function or another VU
execution function.

NEVER reference __VU or __ITER at module/global scope.

For example, this is valid:

export default function () {{
    const transactionId = `test-transaction-${{__VU}}-${{__ITER}}`;
}}

This is invalid:

const transactionId = `test-transaction-${{__VU}}-${{__ITER}}`;

export default function () {{
    ...
}}

REQUEST
-------

Use an appropriate HTTP method based on the supplied API information.

If the exact method is not explicitly provided and cannot be reliably
determined, use POST only when the scenario clearly represents an
operation such as payment or fund transfer, and document the assumption
in a comment.

Do not invent undocumented headers except standard headers such as:

Content-Type: application/json

VALIDATION
----------

Do not assume an undocumented response JSON structure.

Do NOT generate checks such as:

r.json('status') === 'success'

unless the user explicitly supplied that response contract.

At minimum, validate that the HTTP request received a response:

check(response, {{
    'HTTP response received': (r) => r.status > 0,
}});

For an expected successful HTTP status, use a configurable expected
status:

const EXPECTED_STATUS = Number(__ENV.EXPECTED_STATUS || 200);

check(response, {{
    'HTTP status is expected': (r) => r.status === EXPECTED_STATUS,
}});

PERFORMANCE CONFIGURATION
-------------------------

Include a reasonable timeout.

Include useful tags for:

application
scenario
api

Use k6-compatible options only.

The script should be suitable for execution with:

BASE_URL=http://localhost:8000 \\
VUS=10 \\
DURATION=30s \\
k6 run script.js

Do not include shell commands in the generated JavaScript.

OUTPUT
------

Return ONLY the complete k6 JavaScript source code.
"""
        elif tool == "jmeter":
            return f"""
Generate a production-quality Apache JMeter test plan in valid JMX XML format.

TEST CONTEXT
------------
Application: {application}
Scenario: {scenario}
API/Service: {api_name}

IMPORTANT REQUIREMENTS
----------------------

1. Generate ONLY valid Apache JMeter JMX XML.
2. Do not use Markdown code fences.
3. Do not generate Python, Java, Groovy, JavaScript, k6, Gatling,
   Flask, FastAPI, or another framework.
4. The output must be directly loadable as a JMeter .jmx test plan.
5. Do not include explanatory text before or after the XML.
6. Do not invent credentials, secrets, or undocumented API contracts.
7. Do not use fake external production domains.

REQUIRED JMX STRUCTURE
----------------------

The XML must contain a valid JMeter test-plan hierarchy including:

- jmeterTestPlan as the root element
- TestPlan
- ThreadGroup
- HTTPSamplerProxy
- the required hashTree elements that form the JMeter hierarchy

The structure should follow the normal JMeter JMX hierarchy:

jmeterTestPlan
    └── hashTree
        ├── TestPlan
        └── hashTree
            ├── ThreadGroup
            └── hashTree
                └── HTTPSamplerProxy
                └── hashTree

The TestPlan, ThreadGroup, and HTTPSamplerProxy must be represented
as actual JMeter XML elements, not as comments or textual descriptions.

THREAD CONFIGURATION
--------------------

Configure the ThreadGroup using reasonable performance-test settings.

Use configurable or clearly identifiable values for:

- Number of threads/users
- Ramp-up period
- Loop count

Do not invent excessive load values.

REQUEST CONFIGURATION
---------------------

Create an HTTPSamplerProxy representing the API/service under test.

Use an appropriate HTTP method.

If the exact HTTP method is not explicitly supplied:

- Use POST for operations such as payment, fund transfer, transaction
  submission, login submission, or other state-changing operations.
- Use GET for read-only operations such as account balance retrieval
  when that is clearly implied by the scenario.

Do not invent undocumented authentication or credentials.

Use configurable/local test values when the exact API contract is
unknown.

For HTTP requests, configure the server/host and path as test
configuration rather than using fake production domains.

Use a local/test-friendly placeholder such as:

localhost

and an appropriate configurable path.

Do not claim that an invented path is a real production API contract.

JMeter XML must contain the required HTTPSamplerProxy attributes and
configuration properties needed for a valid JMeter HTTP request.

VALID JMX XML
-------------

The XML must be well-formed and parseable.

Use valid JMeter XML syntax and standard JMeter component properties.

Do not include:

- Java source code
- Groovy scripts
- Java imports
- Python code
- Markdown
- fake external production URLs
- explanatory prose outside the XML

OUTPUT
------

Return ONLY the complete JMeter JMX XML source.

The result must be suitable for saving directly as:

test_plan.jmx

and opening in Apache JMeter.
"""
        
        else:
            return f"""
Generate a production-quality {tool} performance-testing artifact.

Application: {application}
Scenario: {scenario}
API/Service: {api_name}

Requirements:
- Generate only valid {tool} source code.
- Do not use Markdown code fences.
- Do not invent credentials or secrets.
- Do not invent undocumented API response contracts.
- Do not use fake external production domains as if they were real.
- Prefer configurable environment/test parameters.
- The artifact must be suitable for execution by the corresponding
  performance-testing tool.
- Include the application, scenario, and API context in the artifact
  where appropriate.

Return ONLY the artifact source code.
"""

    @staticmethod
    def _clean_response(text):
        text = text.strip()

        if text.startswith("```"):
            first_newline = text.find("\n")

            if first_newline != -1:
                text = text[first_newline + 1:]

        if text.endswith("```"):
            text = text[:-3]

        return text.strip()

    @staticmethod
    def _validate_jmeter(content):
        if not content:
            return False

        stripped = content.lstrip()

        if not (
            stripped.startswith("<?xml")
            or stripped.startswith("<jmeterTestPlan")
        ):
            return False

        required_elements = [
            "<jmeterTestPlan",
            "<hashTree",
            "<TestPlan",
            "<ThreadGroup",
            "<HTTPSamplerProxy",
        ]

        for element in required_elements:
            if element not in content:
                return False

        lower_content = content.lower()

        forbidden_patterns = [
            "public class",
            "import org.apache.jmeter",
            "org.apache.jmeter",
            "groovy",
            "java.io.",
            "```",
        ]

        for pattern in forbidden_patterns:
            if pattern.lower() in lower_content:
                return False

        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            return False

        if root.tag != "jmeterTestPlan":
            return False

        test_plan = root.find(".//TestPlan")
        thread_group = root.find(".//ThreadGroup")
        http_sampler = root.find(".//HTTPSamplerProxy")

        if test_plan is None:
            return False

        if thread_group is None:
            return False

        if http_sampler is None:
            return False

        return True

    @staticmethod
    def _validate_k6(content):
        if not content:
            return False

        lower_content = content.lower()

        has_k6_import = (
            "from 'k6'" in content
            or 'from "k6"' in content
        )

        has_http_import = (
            "from 'k6/http'" in content
            or 'from "k6/http"' in content
        )

        has_default_function = (
            "export default function" in content
        )

        # k6 execution-context variables are only available during
        # VU execution and must not be referenced at module scope.
        if has_default_function:
            default_function_index = content.find(
                "export default function"
            )

            module_scope = content[:default_function_index]

            if "__VU" in module_scope or "__ITER" in module_scope:
                return False

        has_http_usage = (
            "http." in content
        )

        has_check_usage = (
            "check(" in content
        )

        has_options = (
            "export const options" in content
            or "export let options" in content
        )

        has_base_url_configuration = (
            "__ENV.BASE_URL" in content
        )

        forbidden_patterns = [
            "```",
            "from flask",
            "from fastapi",
            "import requests",
            "public class",
            "org.apache.jmeter",
            "https://api.example.com",
            "https://yourbank.com",
        ]

        for pattern in forbidden_patterns:
            if pattern.lower() in lower_content:
                return False

        if not has_k6_import:
            return False

        if not has_http_import:
            return False

        if not has_default_function:
            return False

        if not has_http_usage:
            return False

        if not has_check_usage:
            return False

        if not has_options:
            return False

        if not has_base_url_configuration:
            return False

        if "http.post(" not in content and "http.get(" not in content:
            return False

        if "api.example.com" in lower_content:
            return False

        if "yourbank.com" in lower_content:
            return False

        if re.search(
            r"r\.json\s*\(\s*['\"]status['\"]\s*\)",
            content,
        ):
            return False

        return True

    @staticmethod
    def _validate_gatling(content):
        if not content:
            return False

        lower_content = content.lower()

        has_scala_structure = (
            "class " in content
            and "Simulation" in content
        )

        has_gatling_import = "io.gatling" in content

        has_http_usage = (
            "http(" in content
            or "httpProtocol" in content
        )

        forbidden_patterns = [
            "```",
            "public class",
            "import requests",
            "from flask",
            "jmeterTestPlan",
            "import org.apache.jmeter",
            "https://api.example.com",
            "https://yourbank.com",
        ]

        for pattern in forbidden_patterns:
            if pattern.lower() in lower_content:
                return False

        return (
            has_scala_structure
            and has_gatling_import
            and has_http_usage
        )