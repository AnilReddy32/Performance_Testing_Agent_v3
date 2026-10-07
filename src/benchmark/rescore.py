"""
rescore.py

Re-evaluates the agent outputs already captured in benchmark_results.json
against the CURRENT evaluator.py, without re-running the ADK agent.

Useful after editing evaluator.py: lets you see the effect of the change
on pass/fail counts in seconds, instead of waiting for a full agent rerun.

Usage:
    python rescore.py
    python rescore.py --category test_execution
    python rescore.py --results benchmark_results.json --category monitoring
    python rescore.py --write rescored_results.json
"""

import argparse
import json
from pathlib import Path

from evaluator import evaluate_case

ROOT = Path(__file__).resolve().parent


def load_original_cases():
    """
    benchmark_results.json stores a SLIMMED DOWN version of each case
    (id, category, scenario, user_query, expected_agent, expected_tool,
    attempts, ...) - it does NOT preserve the original test case's
    "evaluation" block (required_agent, required_tool, must_not_hallucinate,
    must_preserve_execution_mode). evaluator.py depends on that block.

    Without it, evaluation.get("required_agent", "") silently returns ""
    and "" in text is always True - every case would falsely look like
    it matches the required agent. So we re-load the real test case
    files from test_cases/ and use THOSE (merged with the stored attempt
    outputs) as the source of truth for rescoring.
    """
    originals = {}
    for path in (ROOT / "test_cases").rglob("TC*.json"):
        case = json.loads(path.read_text(encoding="utf-8"))
        originals[case["id"]] = case
    return originals


def rescore_case(result_case, original_case):
    """
    Re-run evaluate_case() against every attempt's already-captured
    output, using the current evaluator.py and the ORIGINAL test case's
    full schema (including its "evaluation" requirements block, which
    the results file does not retain).

    total_attempts is left as the actual number of attempts that were
    historically executed - rescoring judges those same runs under
    new logic, it doesn't simulate what a rerun would have done.
    """

    attempts = result_case.get("attempts", [])
    new_attempts = []

    for attempt in attempts:
        output = attempt.get("execution", {}).get("output", "")
        new_eval = evaluate_case(original_case, output)

        new_attempt = dict(attempt)
        new_attempt["evaluation"] = new_eval
        new_attempts.append(new_attempt)

    pass_at_k = any(a["evaluation"].get("passed", False) for a in new_attempts)

    final_attempt = new_attempts[-1] if new_attempts else {"evaluation": {}}
    final_score = final_attempt["evaluation"].get("score", 0)

    rescored = dict(result_case)
    rescored["attempts"] = new_attempts
    rescored["pass_at_k"] = pass_at_k
    rescored["final_status"] = "PASS" if pass_at_k else "FAIL"
    rescored["final_score"] = final_score

    return rescored


def summarize(results):
    executed = [
        r for r in results
        if r["final_status"] in ["PASS", "FAIL"]
    ]
    passed = [r for r in executed if r["final_status"] == "PASS"]
    failed = [r for r in executed if r["final_status"] == "FAIL"]

    total_attempts = sum(r.get("total_attempts", 0) for r in executed)
    pass_at_k = sum(bool(r.get("pass_at_k", False)) for r in executed)

    return {
        "cases": len(results),
        "executed": len(executed),
        "passed": len(passed),
        "failed": len(failed),
        "total_attempts": total_attempts,
        "pass_rate": round((len(passed) / len(executed) * 100) if executed else 0, 2),
        "pass_at_k": round((pass_at_k / len(executed) * 100) if executed else 0, 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Rescore captured benchmark outputs against the current evaluator.py")
    parser.add_argument("--results", default="benchmark_results.json", help="Existing results file to rescore")
    parser.add_argument("--category", help="Only rescore cases in this category, e.g. test_execution")
    parser.add_argument("--write", help="Optional: write the rescored full results to this file")
    args = parser.parse_args()

    results_path = ROOT / args.results
    data = json.loads(results_path.read_text(encoding="utf-8"))

    cases = data.get("cases", [])

    if args.category:
        cases = [c for c in cases if c.get("category") == args.category]

    if not cases:
        print("No matching cases found.")
        return

    originals = load_original_cases()

    missing = [c["id"] for c in cases if c["id"] not in originals]
    if missing:
        print(
            f"WARNING: {len(missing)} case id(s) not found under test_cases/ "
            f"- skipping (cannot rescore without the original evaluation block): "
            f"{missing[:10]}{' ...' if len(missing) > 10 else ''}"
        )
        cases = [c for c in cases if c["id"] not in missing]

    rescored_cases = [rescore_case(c, originals[c["id"]]) for c in cases]
    summary = summarize(rescored_cases)

    label = f" ({args.category})" if args.category else ""
    print(f"\nRESCORED SUMMARY{label}")
    print("=" * 60)
    print(json.dumps(summary, indent=2))

    # Quick list of flips vs the original stored result, so you can
    # see exactly which cases changed under the new evaluator.
    flips = []
    original_by_id = {c["id"]: c for c in cases}
    for r in rescored_cases:
        orig = original_by_id.get(r["id"], {})
        if orig.get("final_status") != r["final_status"]:
            flips.append((r["id"], orig.get("final_status"), r["final_status"]))

    if flips:
        print("\nCases that changed status under the new evaluator:")
        for case_id, before, after in flips:
            print(f"  {case_id}: {before} -> {after}")
    else:
        print("\nNo cases changed status under the new evaluator.")

    if args.write:
        out_path = ROOT / args.write
        out_data = dict(data)
        # If filtered by category, only replace those cases in-place
        if args.category:
            rescored_by_id = {c["id"]: c for c in rescored_cases}
            all_cases = data.get("cases", [])
            merged = [rescored_by_id.get(c["id"], c) for c in all_cases]
            out_data["cases"] = merged
            out_data["summary"] = summarize(merged)
        else:
            out_data["cases"] = rescored_cases
            out_data["summary"] = summary

        out_path.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
        print(f"\nWrote rescored results to {out_path}")


if __name__ == "__main__":
    main()