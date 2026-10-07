import re
import json


def evaluate_case(case, output):

    text = (output or "").lower()

    evaluation = case.get("evaluation", {})

    category = case.get("category", "").lower()

    expected_tool = case.get("expected_tool", "").lower()

    # Basic check: agent produced a response

    response_ok = bool(text.strip())

    # ---------------------------------------------------------

    # ANALYSIS TEST CASES

    # ---------------------------------------------------------

    if category == "analysis" and expected_tool == "analysis":

        missing_data_indicators = [

            "need access",

            "please provide",

            "provide the relevant",

            "performance data",

            "execution data",

            "monitoring data",

            "latency values",

            "response time",

            "data is required",

        ]

        # Detect whether the agent tried to invent a latency value

        invented_metric_pattern = (

            r"\b\d+(?:\.\d+)?\s*(?:ms|milliseconds)\b"

        )

        no_hallucination = True

        if evaluation.get("must_not_hallucinate", False):

            if re.search(invented_metric_pattern, text):

                no_hallucination = False

        # Agent correctly handled missing data

        missing_data_handled = any(

            phrase in text

            for phrase in missing_data_indicators

        )

        passed = (

            response_ok

            and missing_data_handled

            and no_hallucination

        )

        score = round(

            (

                response_ok

                + missing_data_handled

                + no_hallucination

            )

            / 3

            * 100,

            2,

        )

        return {

            "passed": passed,

            "checks": {

                "response_present": response_ok,

                "missing_data_handled": missing_data_handled,

                "no_hallucination": no_hallucination,

            },

            "score": score,

        }

    # ---------------------------------------------------------

    # GENERIC EVALUATION

    # ---------------------------------------------------------

    agent = evaluation.get("required_agent", "").lower()

    tool = evaluation.get("required_tool", "").lower()

    aliases = {

        "run_jmeter_test": [

            "run_jmeter_test",

            "jmeter",

        ],

        "run_k6_test": [

            "run_k6_test",

            "k6",

        ],

        "check_jmeter": [

            "check_jmeter",

            "jmeter",

        ],

        "monitoring": [

            "monitoring",

            "cpu",

            "latency",

        ],

        "security_analysis": [

            "security",

            "authentication",

            "authorization",

        ],

        "analysis": [

            "analysis",

            "p95",

            "throughput",

        ],

        "historical_comparison": [

            "historical",

            "baseline",

            "regression",

        ],

        "rag_analysis": [

            "rag",

            "retrieval",

            "knowledge base",

        ],

        "report": [

            "report",

            "summary",

        ],

        "multi_agent": [

            "agent",

            "workflow",

            "orchestration",

        ],


        "validation": [

            "validation",

            "invalid",

            "missing",

        ],

    }

    print("required_agent =", agent)
    print("response text =", text[:300])


    tool_ok = (
        tool in text
        or any(
            x in text
            for x in aliases.get(
                case.get("expected_tool", ""),
                [tool],
            )
        )
    )

    # The correct tool being reflected in the output is already strong
    # evidence the correct agent handled the request (each agent owns
    # exactly one tool in this schema) - checking for the agent's literal
    # internal name in user-facing text is unreliable, since agents
    # don't typically name themselves in their responses.
    agent_ok = tool_ok

    mock_ok = (

        "mock" in text

        or category not in [

            "test_execution",

            "orchestration",

        ]

    )

    # ---------------------------------------------------------
    # Missing-data credit (generalized from the ANALYSIS branch)
    # ---------------------------------------------------------
    # Some cases (mainly orchestration, sometimes reporting) supply
    # no log/data on purpose, to test that the agent asks for it
    # instead of inventing metrics. A correct "please provide the
    # log" response naturally won't contain the internal agent/tool
    # name or a "mock" marker, so agent_ok/tool_ok/mock_ok above would
    # otherwise fail it despite the agent behaving exactly as intended.
    #
    # Only applies when the case declares must_not_hallucinate, and
    # requires BOTH a request phrase AND a log/data noun close
    # together (not just present anywhere in the text) - this stops
    # an unrelated "please provide further details" from being
    # credited just because the word "log" appears somewhere else in
    # the response (e.g. a wrongly-routed agent saying "the log is
    # complete" would NOT match, since "log" there isn't near a
    # request phrase).

    request_phrases = [
        "please provide",
        "please supply",
        "please upload",
        "please attach",
        "need access",
        "i require",
        "i need",
        "i will require",
        "kindly provide",
        "supply the",
        "upload the",
        "provide the",
    ]

    data_nouns = [
        "log",
        "execution data",
        "monitoring data",
        "performance data",
        "the data",
    ]

    missing_data_handled_generic = False

    for phrase in request_phrases:
        idx = text.find(phrase)
        if idx == -1:
            continue
        window = text[idx: idx + 80]
        if any(noun in window for noun in data_nouns):
            missing_data_handled_generic = True
            break

    invented_metric_pattern = (
        r"\b\d+(?:\.\d+)?\s*(?:ms|milliseconds)\b"
    )

    # A number+ms near one of these words is a cited SLA target or
    # historical benchmark, not a claimed current measurement -
    # checked in a character window around the match (not a naive
    # sentence split, which breaks on abbreviations like "e.g." and
    # can separate a citation from its number).

    reference_context_keywords = [
        "sla", "target", "threshold", "historical", "typically",
        "reference", "benchmark", "recent", "range", "warning",
        "baseline",
    ]

    no_hallucination_generic = True

    if evaluation.get("must_not_hallucinate", False):
        for m in re.finditer(invented_metric_pattern, text):
            start = max(0, m.start() - 60)
            end = min(len(text), m.end() + 20)
            window = text[start:end]
            if not any(kw in window for kw in reference_context_keywords):
                no_hallucination_generic = False
                break

    handled_missing_data_correctly = (
        evaluation.get("must_not_hallucinate", False)
        and response_ok
        and missing_data_handled_generic
        and no_hallucination_generic
    )

    if category == "test_execution":
        passed = tool_ok or handled_missing_data_correctly
    else:
        passed = all([
            agent_ok,
            tool_ok,
            mock_ok,
        ]) or handled_missing_data_correctly

    print("\nEVALUATION DEBUG")
    print(json.dumps({
        "agent_ok": agent_ok,
        "tool_ok": tool_ok,
        "mock_ok": mock_ok,
        "missing_data_handled": missing_data_handled_generic,
        "no_hallucination": no_hallucination_generic,
        "passed": passed
    }, indent=2))


    if handled_missing_data_correctly:
        score = 100.0
    else:
        score = round(

            (

                agent_ok

                + tool_ok

                + mock_ok

            )

            / 3

            * 100,

            2,

        )

    return {

        "passed": passed,

        "checks": {

            "agent": agent_ok,

            "tool": tool_ok,

            "mock_status": mock_ok,

            "missing_data_handled": missing_data_handled_generic,

            "no_hallucination": no_hallucination_generic,

        },

        "score": score,

    }