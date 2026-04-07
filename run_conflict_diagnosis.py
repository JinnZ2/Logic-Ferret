# run_conflict_diagnosis.py
# ============================================================
# Standalone runner for the Conflict Diagnosis Framework.
# The ferret goes in. The truth comes out.
#
# Usage:
#   python run_conflict_diagnosis.py <text_file> [--table] [--flow] [--json]
#
# Modes:
#   --table   Diagnostic table (layer signals + evidence)
#   --flow    Flowchart trace (the ferret's tunnel path)
#   --json    Raw JSON (for pipelines, LLMs, downstream tools)
#   (no flag) Table + flowchart
# ============================================================

import sys
import json

from sensor_suite.sensors.conflict_diagnosis import (
    diagnose,
    print_diagnosis_table,
    print_flowchart,
)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Logic Ferret -- Conflict Diagnosis Framework")
        print("\"The problem is never what it claims to be.\"")
        print()
        print("Usage: python run_conflict_diagnosis.py <text_file> [options]")
        print()
        print("Options:")
        print("  --table   Diagnostic table (signals + evidence)")
        print("  --flow    Flowchart trace (tunnel path)")
        print("  --json    Raw JSON output")
        print("  (no flag) Table + flowchart")
        sys.exit(0)

    filepath = sys.argv[1]
    flags = set(sys.argv[2:])

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        sys.exit(1)

    if not text.strip():
        print("Empty file. The ferret needs something to sniff.")
        sys.exit(1)

    if "--json" in flags:
        result = diagnose(text)
        for layer in result["layers"]:
            layer["matches"] = layer["matches"][:10]
        print(json.dumps(result, indent=2))
        return

    show_table = "--table" in flags or not flags
    show_flow = "--flow" in flags or not flags

    if show_table:
        print_diagnosis_table(text)

    if show_flow:
        print_flowchart(text)


if __name__ == "__main__":
    main()
