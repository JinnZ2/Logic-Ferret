"""
Tests for the legacy/ quarantine.

legacy/ holds superseded files that are kept rather than deleted,
because the falsified claim is itself the record (see legacy/README.md).
That only works if two properties hold:

  1. The quarantine is INERT. Legacy files must not be importable by
     live code or shipped by packaging. A superseded sensor that is
     still reachable is worse than a deleted one -- it reads as
     current, and in this repo one of them carried an inverted score
     polarity for a year.

  2. The record stays COMPLETE. Every file in legacy/ must be
     documented in legacy/README.md, and every superseding module it
     names must actually exist. A quarantine that accumulates
     undocumented files is a junk drawer, not a lineage record.

Plus regression pins on the two specific claims the quarantine
documents -- the polarity invariant and the C3 weight table -- so that
an edit which silently reverts either one fails here.

Run directly:
    python tests/test_legacy_quarantine.py
"""
import sys, os, re, ast, glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
LEGACY = os.path.join(REPO_ROOT, "legacy")

sys.path.insert(0, REPO_ROOT)


def legacy_files():
    return sorted(
        os.path.basename(p) for p in glob.glob(os.path.join(LEGACY, "*"))
        if os.path.isfile(p) and os.path.basename(p) != "README.md"
    )


def live_python_files():
    """Every .py file in the repo that is not legacy/ and not a test."""
    out = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [
            d for d in dirnames
            if d not in {".git", "__pycache__", "legacy", "tests"}
        ]
        for fn in filenames:
            if fn.endswith(".py"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


# ----------------------------------------------------------------------
# 1. The quarantine is inert
# ----------------------------------------------------------------------

def test_legacy_directory_exists_and_is_populated():
    print("[test_legacy_directory_exists_and_is_populated]")
    assert os.path.isdir(LEGACY), "legacy/ directory missing"
    files = legacy_files()
    assert files, "legacy/ has no quarantined files"
    print(f"  {len(files)} quarantined file(s): {', '.join(files)}")
    print("  PASS")


def test_legacy_is_not_a_package():
    """No __init__.py, so setup.py's find_packages() cannot ship it and
    `import legacy.<x>` cannot resolve it as a package submodule."""
    print("[test_legacy_is_not_a_package]")
    init = os.path.join(LEGACY, "__init__.py")
    assert not os.path.exists(init), (
        "legacy/__init__.py exists -- the quarantine would be packaged "
        "and importable"
    )
    from setuptools import find_packages
    packages = find_packages(where=REPO_ROOT)
    offenders = [p for p in packages if p == "legacy" or p.startswith("legacy.")]
    assert not offenders, f"find_packages() would ship: {offenders}"
    print(f"  no __init__.py; find_packages() yields {sorted(packages)}")
    print("  PASS")


def test_no_live_module_imports_legacy():
    """The load-bearing property: nothing live reaches into legacy/."""
    print("[test_no_live_module_imports_legacy]")
    quarantined_modules = {
        os.path.splitext(f)[0] for f in legacy_files() if f.endswith(".py")
    }
    for path in live_python_files():
        tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                root = name.split(".")[0]
                assert root != "legacy", (
                    f"{os.path.relpath(path, REPO_ROOT)}:{node.lineno}: "
                    f"live code imports from legacy/ ({name})"
                )
                assert root not in quarantined_modules, (
                    f"{os.path.relpath(path, REPO_ROOT)}:{node.lineno}: "
                    f"imports {name!r}, which now resolves to a quarantined "
                    f"module name"
                )
    print(f"  {len(live_python_files())} live module(s) clean of legacy imports")
    print("  PASS")


# ----------------------------------------------------------------------
# 2. The record stays complete
# ----------------------------------------------------------------------

def test_every_legacy_file_is_documented():
    """A quarantined file with no entry is an undocumented deletion
    that happens to still be on disk."""
    print("[test_every_legacy_file_is_documented]")
    readme_path = os.path.join(LEGACY, "README.md")
    assert os.path.exists(readme_path), "legacy/README.md missing"
    readme = open(readme_path, encoding="utf-8").read()

    for filename in legacy_files():
        assert f"`{filename}`" in readme, (
            f"{filename} is quarantined but has no entry in legacy/README.md"
        )
        # each entry must carry a verdict, not just a filename mention
        heading = re.search(
            rf"^## `{re.escape(filename)}` -- (.+)$", readme, re.MULTILINE
        )
        assert heading, f"{filename}: no '## `{filename}` -- <verdict>' heading"
        assert heading.group(1).strip(), f"{filename}: empty verdict"
    print(f"  all {len(legacy_files())} file(s) documented with a verdict")
    print("  PASS")


def test_superseding_modules_exist():
    """Every 'Superseded by' / 'Implemented in' pointer must resolve.
    A lineage record pointing at a moved file is worse than none."""
    print("[test_superseding_modules_exist]")
    readme = open(os.path.join(LEGACY, "README.md"), encoding="utf-8").read()
    pointers = re.findall(
        r"^\| (?:Superseded by|Implemented in) \| `([^`]+)` \|$",
        readme,
        re.MULTILINE,
    )
    assert pointers, "no 'Superseded by' / 'Implemented in' rows found"
    for rel in pointers:
        target = os.path.join(REPO_ROOT, rel)
        assert os.path.exists(target), (
            f"legacy/README.md points at {rel}, which does not exist"
        )
    print(f"  {len(pointers)} lineage pointer(s) resolve")
    print("  PASS")


def test_open_questions_section_present():
    """The 'search for unknowns' step of the loop. Losing this section
    is how open questions become rediscovered ones."""
    print("[test_open_questions_section_present]")
    readme = open(os.path.join(LEGACY, "README.md"), encoding="utf-8").read()
    assert "## Open questions" in readme, "Open questions section missing"
    tail = readme.split("## Open questions", 1)[1]
    numbered = re.findall(r"^\d+\. ", tail, re.MULTILINE)
    assert numbered, "Open questions section is empty"
    print(f"  {len(numbered)} open question(s) recorded")
    print("  PASS")


# ----------------------------------------------------------------------
# 3. Regression pins on the documented claims
# ----------------------------------------------------------------------

def test_sensor_polarity_invariant():
    """The claim the quarantine exists to record: higher score = more
    distortion detected, suite-wide. The legacy copy has the inverted
    form; the live one must not."""
    print("[test_sensor_polarity_invariant]")
    from sensor_suite.sensors import logic_fallacy_ferret

    clean = "The report was published on Tuesday. It lists three findings."
    loaded = (
        "Everyone knows this. Only an idiot would disagree. "
        "Either you support us or you support failure. "
        "Experts say so, so it must be true."
    )
    clean_score, _ = logic_fallacy_ferret.assess(clean)
    loaded_score, _ = logic_fallacy_ferret.assess(loaded)

    assert loaded_score >= clean_score, (
        f"polarity inverted: fallacy-loaded text scored {loaded_score} "
        f"vs clean {clean_score} -- higher must mean more detected"
    )
    assert 0.0 <= clean_score <= 1.0 and 0.0 <= loaded_score <= 1.0

    # and the legacy copy must still carry the falsified form, since
    # that is the whole point of keeping it
    legacy_src = open(
        os.path.join(LEGACY, "Logic_fallacy_ferret.py"), encoding="utf-8"
    ).read()
    assert "1.0 - min(" in legacy_src, (
        "legacy/Logic_fallacy_ferret.py no longer contains the inverted "
        "score it was kept to document"
    )
    print(f"  clean={clean_score}, loaded={loaded_score}; legacy inversion intact")
    print("  PASS")


def test_original_weight_hypothesis_survives():
    """legacy/weights.txt is the only written justification for seven of
    the eight C3 weights. Pin them so a silent retune is visible."""
    print("[test_original_weight_hypothesis_survives]")
    from sensor_suite.sensors.truth_integrity_score import _WEIGHTS

    original = {
        "Propaganda Tone": 1.2,
        "Reward Manipulation": 1.0,
        "False Urgency": 1.1,
        "Gatekeeping": 1.3,
        "Narrative Fragility": 1.4,
        "Propaganda Bias": 1.5,
        "Agency Score": 1.6,
    }
    for name, weight in original.items():
        assert name in _WEIGHTS, f"{name} dropped from _WEIGHTS"
        assert _WEIGHTS[name] == weight, (
            f"{name}: weight changed {weight} -> {_WEIGHTS[name]}; "
            f"update legacy/README.md if this is intentional"
        )

    # the one documented extension: above the entire original scale
    assert _WEIGHTS["Discourse Collapse"] == 2.0
    assert _WEIGHTS["Discourse Collapse"] > max(original.values()), (
        "Discourse Collapse must outrank every original weight -- it is "
        "the only BLACK-tier sensor"
    )

    # the ordering hypothesis from weights.txt, still intact
    assert (
        _WEIGHTS["Agency Score"]
        > _WEIGHTS["Propaganda Bias"]
        > _WEIGHTS["Narrative Fragility"]
        > _WEIGHTS["Gatekeeping"]
        > _WEIGHTS["Propaganda Tone"]
        > _WEIGHTS["False Urgency"]
        > _WEIGHTS["Reward Manipulation"]
    ), "the original weight ordering no longer holds"
    print(f"  7 original weights unchanged; Discourse Collapse extends to 2.0")
    print("  PASS")


def test_no_duplicate_sensor_modules():
    """The hazard propaganda_tone.py demonstrated: two importable copies
    of one sensor, where editing the wrong one is a silent no-op."""
    print("[test_no_duplicate_sensor_modules]")
    seen = {}
    for path in live_python_files():
        rel = os.path.relpath(path, REPO_ROOT)
        seen.setdefault(os.path.basename(path), []).append(rel)

    sensors_dir = os.path.join(REPO_ROOT, "sensor_suite", "sensors")
    sensor_names = {
        os.path.basename(p) for p in glob.glob(os.path.join(sensors_dir, "*.py"))
        if os.path.basename(p) != "__init__.py"
    }
    for name in sorted(sensor_names):
        paths = seen.get(name, [])
        # truth_integrity_score.py at root is a documented re-export shim
        real = [p for p in paths if p != "truth_integrity_score.py"]
        assert len(real) == 1, (
            f"{name} exists at multiple live paths: {real} -- "
            f"one of them is a stale duplicate"
        )
    print(f"  {len(sensor_names)} sensor(s), no live duplicates")
    print("  PASS")


if __name__ == "__main__":
    test_legacy_directory_exists_and_is_populated()
    test_legacy_is_not_a_package()
    test_no_live_module_imports_legacy()
    test_every_legacy_file_is_documented()
    test_superseding_modules_exist()
    test_open_questions_section_present()
    test_sensor_polarity_invariant()
    test_original_weight_hypothesis_survives()
    test_no_duplicate_sensor_modules()
    print("\nall legacy quarantine tests passed.")
