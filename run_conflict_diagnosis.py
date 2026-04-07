# run_conflict_diagnosis.py
#
# Standalone runner for the Conflict Diagnosis Framework.
# Usage:
#   python run_conflict_diagnosis.py path/to/text.txt [--table] [--flow] [--json]
#
# Modes:
#   --table  Print the diagnostic table (default)
#   --flow   Print the step-by-step flowchart
#   --json   Print raw JSON output for programmatic use
#   (no flag defaults to both table + flowchart)

import sys
import json

from sensor_suite.sensors.conflict_diagnosis import (
    diagnose,
    print_diagnosis_table,
    print_flowchart,
)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Conflict Diagnosis Framework -- Logic Ferret")
        print()
        print("Usage: python run_conflict_diagnosis.py <text_file> [options]")
        print()
        print("Options:")
        print("  --table   Show diagnostic table")
        print("  --flow    Show flowchart trace")
        print("  --json    Output raw JSON diagnosis")
        print("  (no flag) Show table + flowchart")
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
        print("File is empty.")
        sys.exit(1)

    if "--json" in flags:
        result = diagnose(text)
        # Convert match lists to keep JSON clean
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
