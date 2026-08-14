"""
Integrity tests for the knowledge/ package.

Two jobs:

1. REGRESSION GUARD. Every operational module in knowledge/ was
   committed to main through a pipeline that mangled its Python
   structure (see the reconstruction log in CLAUDE.md): module
   docstring delimiters commented out, Markdown fence markers
   embedded in the source, smart/curly typography used as string
   delimiters, and all indentation stripped. Each of those four
   damage signatures is asserted against here, for every file, so
   a re-run of the same pipeline fails loudly instead of landing
   another unparseable file on main.

2. SMOKE TEST. The two most recently reconstructed modules
   (shadow_catalog, recontextualizer) are exercised behaviorally
   so "it parses" is not mistaken for "it works".

The operational modules use absolute imports of each other
(`from scope_mapper import ...`) and are authored to run standalone
from the knowledge/ directory. They are therefore loaded here by
file path rather than as package submodules -- the same convention
knowledge/__init__.py documents.

Run directly:
    python tests/test_knowledge_integrity.py
"""
import sys, os, ast, glob, json, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
KNOWLEDGE = os.path.join(REPO_ROOT, "knowledge")

# Modules that carry an `if __name__ == "__main__":` demo block. Parsing
# is necessary but not sufficient -- the demo blocks are what actually
# proved the reconstructions correct, so they stay under test.
WITH_MAIN = [
    "application_builder.py",
    "edge_explorer.py",
    "interactive_navigator.py",
    "knowledge_liberation.py",
    "recontextualizer.py",
    "scope_mapper.py",
    "shadow_catalog.py",
]


def knowledge_files():
    return sorted(glob.glob(os.path.join(KNOWLEDGE, "*.py")))


def load_by_path(filename):
    """Load a knowledge/ module by file path, not as a package submodule."""
    path = os.path.join(KNOWLEDGE, filename)
    name = "knowledge_standalone_" + os.path.splitext(filename)[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------------
# REGRESSION GUARD: the four damage signatures
# ----------------------------------------------------------------------

def test_every_module_parses():
    """Damage signature 4 (stripped indentation) always surfaces here."""
    print("[test_every_module_parses]")
    files = knowledge_files()
    assert files, "no .py files found in knowledge/"
    for path in files:
        source = open(path, encoding="utf-8").read()
        try:
            ast.parse(source)
        except SyntaxError as exc:
            raise AssertionError(
                f"{os.path.basename(path)} does not parse: {exc}"
            ) from exc
    print(f"  {len(files)} module(s) parse")
    print("  PASS")


def test_no_commented_out_module_docstring():
    """Damage signature 1: `\"\"\"` opener turned into a `# \"\"\"` comment."""
    print("[test_no_commented_out_module_docstring]")
    for path in knowledge_files():
        first = open(path, encoding="utf-8").readline().strip()
        assert not first.startswith('# "'), (
            f"{os.path.basename(path)}: module docstring opener is commented out"
        )
    print("  no module opens with a commented-out docstring delimiter")
    print("  PASS")


def test_no_markdown_fences():
    """Damage signature 2: ``` markers embedded in the source."""
    print("[test_no_markdown_fences]")
    for path in knowledge_files():
        for lineno, line in enumerate(open(path, encoding="utf-8"), start=1):
            assert "```" not in line, (
                f"{os.path.basename(path)}:{lineno}: Markdown fence marker in source"
            )
    print("  no Markdown fence markers in any module")
    print("  PASS")


def test_ascii_only():
    """Damage signature 3: smart/curly typography, which breaks the file
    when it lands on a string delimiter and is invisible when it does not."""
    print("[test_ascii_only]")
    for path in knowledge_files():
        for lineno, line in enumerate(open(path, encoding="utf-8"), start=1):
            for col, ch in enumerate(line, start=1):
                assert ord(ch) < 128, (
                    f"{os.path.basename(path)}:{lineno}:{col}: "
                    f"non-ASCII character {ch!r} (U+{ord(ch):04X})"
                )
    print("  all modules are pure ASCII")
    print("  PASS")


def test_no_dunder_emphasis_artifact():
    """The mangler rendered __name__/__main__ as Markdown bold
    (**name**/**main**). That parses as a syntax error, but assert it
    by name so the failure message points at the real cause.

    Comment lines are skipped: the reconstruction notes in the repaired
    modules quote the artifact when describing the damage."""
    print("[test_no_dunder_emphasis_artifact]")
    for path in knowledge_files():
        for lineno, line in enumerate(open(path, encoding="utf-8"), start=1):
            if line.lstrip().startswith("#"):
                continue
            for artifact in ("**name**", "**main**"):
                assert artifact not in line, (
                    f"{os.path.basename(path)}:{lineno}: contains {artifact} "
                    f"(Markdown-emphasis mangling of a dunder)"
                )
    print("  no **name**/**main** artifacts outside comments")
    print("  PASS")


def test_main_blocks_execute():
    """Parsing proves structure; running proves the reconstruction.
    Each demo block must exit 0 with an empty stderr."""
    print("[test_main_blocks_execute]")
    for filename in WITH_MAIN:
        path = os.path.join(KNOWLEDGE, filename)
        assert os.path.exists(path), f"{filename} missing from knowledge/"
        result = subprocess.run(
            [sys.executable, path],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"{filename} __main__ exited {result.returncode}:\n"
            f"{result.stderr.rstrip()}"
        )
        assert result.stdout.strip(), f"{filename} __main__ produced no output"
    print(f"  {len(WITH_MAIN)} demo block(s) ran clean")
    print("  PASS")


def test_with_main_list_is_complete():
    """Guard the guard: if a module gains or loses a __main__ block,
    WITH_MAIN must be updated rather than silently drifting."""
    print("[test_with_main_list_is_complete]")
    actual = set()
    for path in knowledge_files():
        source = open(path, encoding="utf-8").read()
        if '__name__ == "__main__"' in source:
            actual.add(os.path.basename(path))
    assert actual == set(WITH_MAIN), (
        f"WITH_MAIN drift -- only in file tree: {sorted(actual - set(WITH_MAIN))}, "
        f"only in WITH_MAIN: {sorted(set(WITH_MAIN) - actual)}"
    )
    print(f"  WITH_MAIN matches the {len(actual)} module(s) that have one")
    print("  PASS")


# ----------------------------------------------------------------------
# SMOKE TEST: shadow_catalog
# ----------------------------------------------------------------------

def test_shadow_catalog_seeds():
    """The seed catalog is the module's whole payload -- if the
    reconstruction dropped a pattern, it shows up as a count change."""
    print("[test_shadow_catalog_seeds]")
    sc = load_by_path("shadow_catalog.py")
    catalog = sc.ShadowCatalog()
    expected = {
        "SEL-001", "SEL-002", "TMP-001", "ONT-001", "ONT-002", "CTX-001",
        "INC-001", "STR-001", "POP-001", "MSR-001", "CAU-001", "INT-001",
    }
    assert set(catalog.patterns) == expected, (
        f"missing: {sorted(expected - set(catalog.patterns))}, "
        f"unexpected: {sorted(set(catalog.patterns) - expected)}"
    )
    # every pattern carries the fields the diagnosis path reads
    for pid, pattern in catalog.patterns.items():
        assert pattern.pattern_id == pid, f"{pid}: id/key mismatch"
        assert isinstance(pattern.category, sc.SilenceCategory), f"{pid}: bad category"
        assert pattern.recognition_cues, f"{pid}: no recognition cues"
        assert pattern.diagnostic_questions, f"{pid}: no diagnostic questions"
        assert pattern.what_is_typically_silent, f"{pid}: nothing declared silent"
        assert pattern.misapplication_risk, f"{pid}: no misapplication risk"
    print(f"  {len(catalog.patterns)} seeded patterns, all fields populated")
    print("  PASS")


def test_shadow_catalog_cue_matching():
    print("[test_shadow_catalog_cue_matching]")
    sc = load_by_path("shadow_catalog.py")
    catalog = sc.ShadowCatalog()

    # "employed adults" is a SEL-001 cue; "leads to" is a CAU-001 cue
    matches = catalog.match_cues(
        "We recruited 273 employed adults via online survey. "
        "Results show childhood trauma leads to increased suicide risk."
    )
    matched_ids = {p.pattern_id for p in matches}
    assert "SEL-001" in matched_ids, f"survivor selection not matched: {matched_ids}"
    assert "CAU-001" in matched_ids, f"causal framing not matched: {matched_ids}"

    # a pattern matches at most once even with several cues present
    assert len(matches) == len(matched_ids), "duplicate pattern in match list"

    # no cues -> no matches, and diagnose() says so rather than crashing
    assert catalog.match_cues("The sky is blue.") == []
    assert "No cataloged silence patterns matched" in catalog.diagnose("The sky is blue.")
    print(f"  cue matching hit {sorted(matched_ids)}; empty case handled")
    print("  PASS")


def test_shadow_catalog_add_and_categories():
    print("[test_shadow_catalog_add_and_categories]")
    sc = load_by_path("shadow_catalog.py")
    catalog = sc.ShadowCatalog()

    selection = catalog.by_category(sc.SilenceCategory.SELECTION)
    assert {p.pattern_id for p in selection} == {"SEL-001", "SEL-002"}

    new = sc.SilencePattern(
        pattern_id="TST-001",
        name="Test pattern",
        category=sc.SilenceCategory.MEASUREMENT,
        description="A pattern added at runtime.",
        recognition_cues=["a very distinctive test cue"],
        diagnostic_questions=["Did this get added?"],
        what_is_typically_silent=["Nothing; this is a test."],
        misapplication_risk="None; this is a test.",
        how_to_surface=["Read the test."],
        common_reframes=["It is a test."],
    )
    catalog.add(new)
    assert catalog.get("TST-001") is new
    assert {p.pattern_id for p in catalog.match_cues("a very distinctive test cue")} == {"TST-001"}

    # duplicate IDs are rejected -- the catalog is meant to grow, not overwrite
    try:
        catalog.add(new)
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate pattern_id was accepted")
    print("  by_category, add(), and duplicate rejection all behave")
    print("  PASS")


def test_shadow_catalog_json_export():
    """export_json is the machine-readable surface other tools consume."""
    print("[test_shadow_catalog_json_export]")
    sc = load_by_path("shadow_catalog.py")
    catalog = sc.ShadowCatalog()
    data = json.loads(catalog.export_json())
    assert set(data) == set(catalog.patterns)
    sample = data["SEL-001"]
    # the enum must serialize to its value, not repr as an Enum member
    assert sample["category"] == "selection", f"category not serialized: {sample['category']!r}"
    assert isinstance(sample["recognition_cues"], list)
    print(f"  {len(data)} patterns export as JSON with enum values flattened")
    print("  PASS")


# ----------------------------------------------------------------------
# SMOKE TEST: recontextualizer
# ----------------------------------------------------------------------

def test_recontextualizer_generates_prompt():
    print("[test_recontextualizer_generates_prompt]")
    rc = load_by_path("recontextualizer.py")
    context = rc.UserContext(
        role=rc.ContextRole.RESEARCHER,
        domain="public health epidemiology",
        location_or_region="a mid-sized city",
        population_of_interest="adults 18-65",
        time_horizon="3-year study window",
        available_resources=["municipal health data"],
        goal="address the original sample's selection bias",
    )
    silence = "Study excluded people in acute crisis (sample is employed/stable)"
    prompt = rc.Recontextualizer().recontextualize(silence, context)

    assert prompt.original_silence == silence
    # the localized question must actually be localized, not a template echo
    assert "a mid-sized city" in prompt.localized_question
    assert "adults 18-65" in prompt.localized_question
    for field_name in ("what_to_observe", "what_to_measure", "who_to_ask", "where_to_look"):
        assert getattr(prompt, field_name), f"{field_name} is empty"
    assert prompt.small_experiment and prompt.build_possibility
    # role-specific branches must fire, not fall through to the generic text
    assert "pilot" in prompt.small_experiment.lower()
    assert context.goal in prompt.build_possibility
    print("  prompt localized to context; role branch fired")
    print("  PASS")


def test_recontextualizer_generic_context():
    """An empty UserContext is the documented default -- it must still
    produce a usable prompt rather than blank-substituted text."""
    print("[test_recontextualizer_generic_context]")
    rc = load_by_path("recontextualizer.py")
    context = rc.UserContext()
    assert context.describe() == "generic context"

    prompt = rc.Recontextualizer().recontextualize("Some detected silence", context)
    assert "your context" in prompt.localized_question
    assert "the people you work with" in prompt.localized_question
    assert prompt.what_to_measure, "generic context produced no measurement suggestions"
    assert "the next few days or weeks" in prompt.small_experiment
    rendered = prompt.format()
    assert "SILENCE: Some detected silence" in rendered
    assert "LOCALIZED QUESTION:" in rendered
    print("  generic context degrades to usable defaults")
    print("  PASS")


def test_recontextualizer_batch():
    print("[test_recontextualizer_batch]")
    rc = load_by_path("recontextualizer.py")
    context = rc.UserContext(role=rc.ContextRole.FIELD_WORKER, domain="community health")
    silences = [
        "Study excluded people in acute crisis",
        "Does NOT distinguish accurate vs. false threat assessment",
    ]
    out = rc.recontextualize_silences(silences, context)
    for i, silence in enumerate(silences, start=1):
        assert f"### Silence {i} of {len(silences)}" in out
        assert silence in out
    assert "role: field_worker" in out
    print(f"  {len(silences)} silences rendered in one batch document")
    print("  PASS")


def test_recontextualizer_covers_every_role():
    """Every ContextRole must be reachable without error -- the role
    branches are long if/elif chains and are easy to break silently."""
    print("[test_recontextualizer_covers_every_role]")
    rc = load_by_path("recontextualizer.py")
    recon = rc.Recontextualizer()
    for role in rc.ContextRole:
        prompt = recon.recontextualize("A silence", rc.UserContext(role=role))
        assert prompt.small_experiment, f"{role.value}: no experiment generated"
        assert prompt.who_to_ask, f"{role.value}: no sources generated"
    print(f"  all {len(list(rc.ContextRole))} roles generate prompts")
    print("  PASS")


if __name__ == "__main__":
    test_every_module_parses()
    test_no_commented_out_module_docstring()
    test_no_markdown_fences()
    test_ascii_only()
    test_no_dunder_emphasis_artifact()
    test_main_blocks_execute()
    test_with_main_list_is_complete()
    test_shadow_catalog_seeds()
    test_shadow_catalog_cue_matching()
    test_shadow_catalog_add_and_categories()
    test_shadow_catalog_json_export()
    test_recontextualizer_generates_prompt()
    test_recontextualizer_generic_context()
    test_recontextualizer_batch()
    test_recontextualizer_covers_every_role()
    print("\nall knowledge integrity tests passed.")
