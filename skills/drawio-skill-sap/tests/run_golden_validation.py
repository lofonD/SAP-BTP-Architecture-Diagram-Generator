#!/usr/bin/env python3
"""Golden validation runner for reference diagrams.

Checks that selected reference diagrams keep stable lint quality. This is a
regression harness around scripts/validate.py JSON output.

Usage:
  python3 tests/run_golden_validation.py
  python3 tests/run_golden_validation.py --update
"""

import argparse
import json
import os
import subprocess
import sys

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_INPUT = 2

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)
SCRIPTS = os.path.join(SKILL_ROOT, "scripts")
BASELINE_PATH = os.path.join(HERE, "golden_validation.json")

DEFAULT_FILES = [
    "SAP_Task_Center_L0.drawio",
    "SAP_Task_Center_L1.drawio",
    "SAP_Task_Center_L2.drawio",
    "SAP_Start_L2.drawio",
    "SAP_Build_Work_Zone_L2.drawio",
    "SAP_Build_Process_Automation_L2.drawio",
    "SAP_Cloud_Identity_Services_Authentication_L2.drawio",
    "SAP_Cloud_Identity_Services_Authorization_L1.drawio",
    "SAP_Cloud_Identity_Services_Identity_Lifecycle_L1.drawio",
    "SAP_Private_Link_Service_L2.drawio",
    "BTP_Reference_Architect_Diagram.drawio",
]


def run_validate(path):
    cmd = [
        sys.executable,
        os.path.join(SCRIPTS, "validate.py"),
        path,
        "--score",
        "--json",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode not in (0, 1):
        return None, f"validate.py failed ({r.returncode}): {r.stderr.strip()}"
    try:
        return json.loads(r.stdout or "{}"), None
    except ValueError as exc:
        return None, f"invalid JSON from validate.py: {exc}"


def collect(reference_dir):
    out = {}
    for rel in DEFAULT_FILES:
        path = os.path.join(reference_dir, rel)
        payload, err = run_validate(path)
        if err:
            return None, f"{rel}: {err}"
        score = payload.get("score") or {}
        summary = payload.get("summary") or {}
        out[rel] = {
            "errors": int(summary.get("errors", 0)),
            "warnings": int(summary.get("warnings", 0)),
            "score": int(score.get("value", 0)),
        }
    return out, None


def main():
    ap = argparse.ArgumentParser(description="Run or update golden validation baseline")
    ap.add_argument("--update", action="store_true", help="recompute and overwrite baseline")
    args = ap.parse_args()

    ref_dir = os.path.join(SKILL_ROOT, "references")
    current, err = collect(ref_dir)
    if err:
        print(f"error: {err}", file=sys.stderr)
        sys.exit(EXIT_INPUT)

    if args.update:
        payload = {
            "files": DEFAULT_FILES,
            "results": current,
        }
        with open(BASELINE_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"updated baseline: {BASELINE_PATH}")
        sys.exit(EXIT_OK)

    if not os.path.exists(BASELINE_PATH):
        print("error: baseline file missing, run with --update first", file=sys.stderr)
        sys.exit(EXIT_INPUT)

    with open(BASELINE_PATH, "r", encoding="utf-8") as f:
        baseline = json.load(f)

    expected = baseline.get("results", {})
    failures = []
    for rel in DEFAULT_FILES:
        exp = expected.get(rel)
        got = current.get(rel)
        if exp is None:
            failures.append(f"missing baseline for {rel}")
            continue
        if got != exp:
            failures.append(f"{rel}: expected {exp}, got {got}")

    if failures:
        print("golden validation: FAIL")
        for item in failures:
            print(f"- {item}")
        sys.exit(EXIT_FAILED)

    print("golden validation: PASS")
    for rel in DEFAULT_FILES:
        r = current[rel]
        print(f"- {rel}: errors={r['errors']} warnings={r['warnings']} score={r['score']}")
    sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()
