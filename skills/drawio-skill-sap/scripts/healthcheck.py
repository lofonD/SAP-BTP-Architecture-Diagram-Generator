#!/usr/bin/env python3
"""Health check for drawio-skill-sap.

Validates runtime prerequisites and smoke-tests core scripts with stable
machine-readable output support.

Usage:
  python3 scripts/healthcheck.py
  python3 scripts/healthcheck.py --json
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

EXIT_OK = 0
EXIT_FAILED = 1

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)
REF_DIR = os.path.join(SKILL_ROOT, "references")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def check_binary(names):
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def main():
    ap = argparse.ArgumentParser(description="Run dependency and smoke checks for drawio-skill-sap")
    ap.add_argument("--json", action="store_true", help="emit JSON report")
    args = ap.parse_args()

    report = {
        "ok": True,
        "checks": [],
    }

    drawio_path = check_binary(["drawio", "draw.io"])
    dot_path = check_binary(["dot"])

    report["checks"].append({
        "name": "drawio-cli",
        "ok": drawio_path is not None,
        "details": drawio_path or "not found on PATH",
    })
    report["checks"].append({
        "name": "graphviz-dot",
        "ok": dot_path is not None,
        "details": dot_path or "not found on PATH",
    })

    sample_drawio = os.path.join(REF_DIR, "SAP_Task_Center_L0.drawio")
    r = run([sys.executable, os.path.join(HERE, "validate.py"), sample_drawio, "--score", "--json"])
    validate_ok = r.returncode in (0, 1)
    validate_payload = None
    if validate_ok:
        try:
            validate_payload = json.loads(r.stdout or "{}")
        except ValueError:
            validate_ok = False
    report["checks"].append({
        "name": "validate-json-smoke",
        "ok": validate_ok,
        "details": validate_payload.get("summary") if isinstance(validate_payload, dict) else "invalid JSON output",
    })

    r = run([sys.executable, os.path.join(HERE, "sap_shapesearch.py"), "work zone", "--limit", "1", "--json"])
    shape_ok = r.returncode == 0
    shape_payload = None
    if shape_ok:
        try:
            shape_payload = json.loads(r.stdout or "{}")
            shape_ok = bool(shape_payload.get("results"))
        except ValueError:
            shape_ok = False
    report["checks"].append({
        "name": "sap-shapesearch-json-smoke",
        "ok": shape_ok,
        "details": (shape_payload.get("results") or [None])[0].get("title") if shape_payload and shape_payload.get("results") else "no result",
    })

    if dot_path is None:
        report["checks"].append({
            "name": "autolayout-json-smoke",
            "ok": False,
            "details": "skipped (Graphviz dot missing)",
        })
    else:
        with tempfile.TemporaryDirectory() as tmp:
            graph_path = os.path.join(tmp, "graph.json")
            out_path = os.path.join(tmp, "layout.drawio")
            with open(graph_path, "w", encoding="utf-8") as f:
                json.dump({
                    "direction": "TB",
                    "nodes": [
                        {"id": "a", "label": "A"},
                        {"id": "b", "label": "B"},
                    ],
                    "edges": [{"source": "a", "target": "b"}],
                }, f)
            r = run([sys.executable, os.path.join(HERE, "autolayout.py"), graph_path, "-o", out_path, "--json"])
            layout_ok = r.returncode == 0 and os.path.exists(out_path)
            layout_payload = None
            if layout_ok:
                try:
                    layout_payload = json.loads(r.stdout or "{}")
                    layout_ok = bool(layout_payload.get("ok"))
                except ValueError:
                    layout_ok = False
            report["checks"].append({
                "name": "autolayout-json-smoke",
                "ok": layout_ok,
                "details": layout_payload.get("direction") if layout_payload else "invalid JSON output",
            })

    report["ok"] = all(c["ok"] for c in report["checks"])

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for c in report["checks"]:
            state = "PASS" if c["ok"] else "FAIL"
            print(f"[{state}] {c['name']}: {c['details']}")
        print("overall: PASS" if report["ok"] else "overall: FAIL")

    sys.exit(EXIT_OK if report["ok"] else EXIT_FAILED)


if __name__ == "__main__":
    main()
