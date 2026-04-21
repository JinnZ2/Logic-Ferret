"""
Run every test_*.py in the tests/ directory as a standalone script,
accumulate pass/fail, and report.

No external runner needed. Matches sibling framework convention
(metabolic-accounting/tests/) -- each test file is directly
executable; this script is the convenience umbrella.

Run from repo root:
    python tests/run_all.py
"""
import sys, os, subprocess, glob, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)


def main() -> int:
    test_files = sorted(
        f for f in glob.glob(os.path.join(HERE, "test_*.py"))
        if os.path.basename(f) != "run_all.py"
    )
    if not test_files:
        print("no test_*.py files found in", HERE)
        return 1

    print(f"running {len(test_files)} test file(s)")
    print("=" * 70)

    passed = []
    failed = []
    start = time.time()

    for path in test_files:
        name = os.path.basename(path)
        print(f"\n--- {name} ---")
        result = subprocess.run(
            [sys.executable, path],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        # stream stdout so individual PASS lines stay visible
        if result.stdout:
            print(result.stdout.rstrip())
        if result.returncode == 0:
            passed.append(name)
        else:
            failed.append(name)
            if result.stderr:
                print("STDERR:")
                print(result.stderr.rstrip())

    elapsed = time.time() - start
    print()
    print("=" * 70)
    print(f"{len(passed)} passed, {len(failed)} failed  ({elapsed:.2f}s)")
    if failed:
        print("failed files:")
        for n in failed:
            print(f"  - {n}")
        return 1
    print("all tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
