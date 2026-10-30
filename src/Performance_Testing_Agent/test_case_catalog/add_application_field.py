"""
One-time script: adds an "application" field to every entry in
performance_tests.json, based on its target_url. Run this once from
wherever performance_tests.json lives.

Usage:
    python add_application_field.py performance_tests.json
"""
import json
import sys

APPLICATION_BY_HOST = {
    "jsonplaceholder.typicode.com": "JSONPlaceholder",
    "dummyjson.com": "DummyJSON",
    "localhost": "Local Banking Mock Platform",
    "127.0.0.1": "Local Banking Mock Platform",
}


def infer_application(target_url: str) -> str:
    for host, application in APPLICATION_BY_HOST.items():
        if host in target_url:
            return application
    return "Unknown"


def main(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        entries = json.load(f)

    changed = 0
    for entry in entries:
        if "application" not in entry:
            entry["application"] = infer_application(entry.get("target_url", ""))
            changed += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
        f.write("\n")

    print(f"Added 'application' to {changed} of {len(entries)} entries.")
    print("Review the result - entries with an unrecognized target_url got 'Unknown'.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_application_field.py performance_tests.json")
        sys.exit(1)
    main(sys.argv[1])