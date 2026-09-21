import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class TestPlanner:
    """
    LLM-driven planner for performance-testing requests.

    Converts a natural-language user request into a structured
    performance-testing plan.
    """

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def plan(self, user_request: str) -> dict:
        """
        Convert a natural-language performance-testing request into
        a structured test plan.

        Args:
            user_request: Natural-language performance-testing request.

        Returns:
            A structured test plan dictionary.
        """

        if not user_request or not user_request.strip():
            return {
                "status": "error",
                "message": "User request cannot be empty.",
            }

        prompt = self._build_prompt(user_request)

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert performance testing planner. "
                        "Convert natural-language performance-testing "
                        "requests into structured JSON plans. "
                        "Do not execute tests and do not fabricate results."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        content = response.choices[0].message.content

        if not content:
            return {
                "status": "error",
                "message": "The planner returned an empty response.",
            }

        content = self._clean_response(content)

        try:
            plan = json.loads(content)
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "The planner returned invalid JSON.",
                "raw_response": content,
            }

        validation_error = self._validate_plan(plan)

        if validation_error:
            return {
                "status": "error",
                "message": validation_error,
                "plan": plan,
            }

        return {
            "status": "success",
            "plan": plan,
        }

    @staticmethod
    def _build_prompt(user_request: str) -> str:
        return f"""
Analyze the following performance-testing request and convert it
into a structured JSON test plan.

USER REQUEST:
{user_request}

Return ONLY valid JSON.

Use exactly these fields:

{{
    "intent": "",
    "test_type": "",
    "tool": "",
    "application": "",
    "scenario": "",
    "api_name": "",
    "users": 0,
    "duration": 0
}}

Rules:

1. intent must be one of:
   - "execute_test"
   - "generate_script"
   - "generate_test_data"
   - "prepare_environment"
   - "invalid"

2. test_type should normally be one of:
   - "load"
   - "stress"
   - "endurance"
   - "spike"
   - "concurrent"
   - "performance"
   - "unknown"

3. tool must normally be one of:
   - "jmeter"
   - "k6"
   - "gatling"

   If the user does not specify a tool, use:
   "jmeter"

4. application:
   Identify the application or system being tested.

   For example:
   "Internet Banking"

5. scenario:
   Identify the business or testing scenario.

   Examples:
   "UPI Payment"
   "Fund Transfer"
   "Login"
   "Account Balance"

6. api_name:
   Identify the API or service being tested.

   If an explicit endpoint is provided, preserve it.

   For example:
   "/api/v1/payment"

   If the exact API endpoint is not provided but the scenario
   clearly identifies the service, use a sensible service name.

7. users:
   - For execute_test requests, extract the number of virtual/concurrent
     users; 5k -> 5000, etc.
   - For generate_test_data requests, use this field to represent the
     requested number of records/data items.
     Examples:
       "Generate 100,000 banking transactions" -> 100000
       "Prepare 5,000 test accounts" -> 5000
       "Generate 10,000 login credentials" -> 10000
   - For other intents, use 0 when a count is not specified.
   - For execute_test requests where users are required but missing,
     use 1.
   - For generate_test_data requests where record count is missing,
     use 100.

8. duration:
   Return duration in seconds.

   Convert:
   - 30 minutes -> 1800
   - 1 hour -> 3600
   - 2 hours -> 7200
   - 30 seconds -> 30

   If duration is not specified and is not required for the
   requested operation, use 0.

   For execution requests where duration is required but missing,
   use 60 seconds as the default.

9. Missing optional information should NOT cause an error.

10. Do not ask questions inside the JSON.

11. Do not invent an API endpoint when the user gives a completely
    unrelated or unsupported request.

12. If the request is not related to performance testing, mark:
    "intent": "invalid"

13. Do not execute anything.

14. Do not generate metrics.

15. Return ONLY the JSON object.
"""


    @staticmethod
    def _clean_response(text: str) -> str:
        """
        Remove accidental Markdown code fences from the LLM response.
        """

        text = text.strip()

        if text.startswith("```"):
            first_newline = text.find("\n")

            if first_newline != -1:
                text = text[first_newline + 1:]

        if text.endswith("```"):
            text = text[:-3]

        return text.strip()

    @staticmethod
    def _validate_plan(plan: dict) -> str | None:
        """
        Validate the planner output.
        """

        if not isinstance(plan, dict):
            return "Planner output must be a JSON object."

        expected_fields = {
            "intent",
            "test_type",
            "tool",
            "application",
            "scenario",
            "api_name",
            "users",
            "duration",
        }

        actual_fields = set(plan.keys())

        if actual_fields != expected_fields:
            missing = expected_fields - actual_fields
            extra = actual_fields - expected_fields

            return (
                "Invalid planner schema. "
                f"Missing fields: {missing}. "
                f"Extra fields: {extra}."
            )

        valid_intents = {
            "execute_test",
            "generate_script",
            "generate_test_data",
            "prepare_environment",
            "invalid",
        }

        if plan["intent"] not in valid_intents:
            return f"Unsupported intent: {plan['intent']}."

        valid_tools = {
            "jmeter",
            "k6",
            "gatling",
        }

        if plan["tool"] not in valid_tools:
            return f"Unsupported performance-testing tool: {plan['tool']}."

        if not isinstance(plan["users"], int):
            return "Users must be an integer."

        if not isinstance(plan["duration"], int):
            return "Duration must be an integer in seconds."

        if plan["users"] < 0:
            return "Users cannot be negative."

        if plan["duration"] < 0:
            return "Duration cannot be negative."

        if plan["intent"] == "execute_test":

            if plan["users"] < 1:
                return "Execution requests require at least one user."

            if plan["duration"] < 1:
                return "Execution requests require a positive duration."

        return None


def plan_test_request(user_request: str) -> dict:
    """
    ADK tool for converting a natural-language performance-testing
    request into a structured test plan.

    Use this tool when the user's request needs to be analyzed
    before selecting the appropriate performance-testing operation.
    """

    planner = TestPlanner()

    return planner.plan(user_request)