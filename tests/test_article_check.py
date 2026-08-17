"""
Tests for practice/article_check.py -- the human critical-thinking check.

The load-bearing property is ORDERING: the tool must not reveal any
machine output until a complete human read exists. Anchoring a reader
to a score and then asking what they think produces agreement, not
judgment, and it would make the whole exercise worthless while still
appearing to work. So `test_machine_read_not_reachable_from_worksheet`
and `test_report_requires_complete_read` are the two that matter most
here; the rest guard the question bank and the comparison arithmetic.

Run directly:
    python tests/test_article_check.py
"""
import sys, os, io, json, subprocess, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
sys.path.insert(0, REPO_ROOT)

from schema_contract import LAYER_NAMES, TIER_LEVELS
from practice.article_check import (
    LAYER_QUESTIONS,
    OPEN_QUESTIONS,
    RATING_SCALE,
    WIDTH,
    AGREE,
    YOU_SAW_MORE,
    FERRET_SAW_MORE,
    HumanRead,
    MachineRead,
    blank_worksheet,
    compare,
    format_report,
    machine_read,
    tier_rank,
)

EXAMPLE = os.path.join(REPO_ROOT, "examples", "offshore_wind_radar.txt")


def a_human_read(**overrides):
    """A complete, valid read. Overrides patch individual layers."""
    ratings = {name: "GREEN" for name in LAYER_NAMES}
    ratings.update(overrides)
    return HumanRead(
        layer_ratings=ratings,
        overall="AMBER",
        answers={"falsifiable": "A published cost breakdown."},
    )


def a_machine_read(**overrides):
    tiers = {name: "GREEN" for name in LAYER_NAMES}
    tiers.update(overrides)
    return MachineRead(
        layer_tiers=tiers,
        layer_hits={name: 0 for name in LAYER_NAMES},
        layer_matches={name: [] for name in LAYER_NAMES},
        overall="AMBER",
        camouflage_score=0.5,
        collapse_alert=False,
    )


# ----------------------------------------------------------------------
# The question bank
# ----------------------------------------------------------------------

def test_one_question_per_diagnosis_layer():
    """The bank must cover the pipeline's layers exactly -- a question
    for a layer that does not exist could never be compared, and a
    layer with no question would silently drop out of the check."""
    print("[test_one_question_per_diagnosis_layer]")
    asked = [q.layer for q in LAYER_QUESTIONS]
    assert len(asked) == len(set(asked)), f"duplicate layer question: {asked}"
    assert set(asked) == set(LAYER_NAMES), (
        f"missing: {sorted(set(LAYER_NAMES) - set(asked))}, "
        f"unknown: {sorted(set(asked) - set(LAYER_NAMES))}"
    )
    assert tuple(asked) == LAYER_NAMES, "question order must match LAYER_NAMES"
    print(f"  {len(asked)} questions, one per layer, in pipeline order")
    print("  PASS")


def test_every_question_is_substantive():
    print("[test_every_question_is_substantive]")
    for q in LAYER_QUESTIONS:
        for field_name in ("ask", "looking_for", "green_looks_like", "red_looks_like"):
            value = getattr(q, field_name)
            assert isinstance(value, str) and len(value) > 30, (
                f"{q.layer}.{field_name}: missing or too short"
            )
        assert "?" in q.ask, f"{q.layer}: ask is not a question"
    for q in OPEN_QUESTIONS:
        assert len(q.ask) > 30 and len(q.why) > 30, f"{q.key}: thin question"
    print(f"  {len(LAYER_QUESTIONS)} layer + {len(OPEN_QUESTIONS)} open questions")
    print("  PASS")


def test_prior_belief_is_asked_first():
    """Asked last it is a rationalization; asked first it is a control.
    The runner relies on OPEN_QUESTIONS[0] being the prior."""
    print("[test_prior_belief_is_asked_first]")
    assert OPEN_QUESTIONS[0].key == "prior", (
        f"OPEN_QUESTIONS[0] is {OPEN_QUESTIONS[0].key!r}; the prior-belief "
        f"question must come first or it measures nothing"
    )
    print("  prior-belief question is first")
    print("  PASS")


def test_falsifiability_question_present():
    """The single most diagnostic item. format_report() calls it out by
    key, so losing it would silently drop that section."""
    print("[test_falsifiability_question_present]")
    keys = {q.key for q in OPEN_QUESTIONS}
    assert "falsifiable" in keys, f"no falsifiability question; have {keys}"
    print(f"  open questions: {sorted(keys)}")
    print("  PASS")


def test_rating_scale_matches_tier_levels():
    print("[test_rating_scale_matches_tier_levels]")
    assert tuple(RATING_SCALE.keys()) == TIER_LEVELS, (
        f"scale {tuple(RATING_SCALE)} diverged from contract {TIER_LEVELS}"
    )
    assert "overall only" in RATING_SCALE["BLACK"].lower()
    print(f"  scale matches TIER_LEVELS: {TIER_LEVELS}")
    print("  PASS")


# ----------------------------------------------------------------------
# Ordering: no machine output before a complete human read
# ----------------------------------------------------------------------

def test_report_requires_complete_read():
    """An unrated layer must raise, not default. Defaulting to GREEN
    would score it as agreement with a quiet sensor -- the reader would
    be credited for a judgment they never made."""
    print("[test_report_requires_complete_read]")
    partial = a_human_read()
    del partial.layer_ratings["Hidden Driver"]
    try:
        compare(partial, a_machine_read())
    except ValueError as exc:
        assert "Hidden Driver" in str(exc)
    else:
        raise AssertionError("incomplete read was accepted")

    bad_tier = a_human_read()
    bad_tier.layer_ratings["Stated Problem"] = "PURPLE"
    try:
        compare(bad_tier, a_machine_read())
    except ValueError as exc:
        assert "PURPLE" in str(exc)
    else:
        raise AssertionError("unknown tier was accepted")
    print("  incomplete and invalid reads both rejected")
    print("  PASS")


def test_black_rejected_per_layer():
    """Only Layer 9 / discourse collapse reaches BLACK. Allowing a human
    to mark a regular layer BLACK would break comparability with the
    sensor signal, which cannot emit it."""
    print("[test_black_rejected_per_layer]")
    read = a_human_read()
    read.layer_ratings["Feedback Loops"] = "BLACK"
    try:
        read.validate()
    except ValueError as exc:
        assert "BLACK" in str(exc)
    else:
        raise AssertionError("per-layer BLACK was accepted")

    # but BLACK remains legal as an overall estimate
    ok = a_human_read()
    ok.overall = "BLACK"
    ok.validate()
    print("  per-layer BLACK rejected; overall BLACK allowed")
    print("  PASS")


def test_machine_read_not_reachable_from_worksheet():
    """The blank worksheet is the pre-read artifact. It must not contain
    any per-article result, and generating it must not require the
    sensor suite at all."""
    print("[test_machine_read_not_reachable_from_worksheet]")
    sheet = blank_worksheet()
    for leak in ("camouflage", "ferret tier", "CALIBRATION", "matched:"):
        assert leak.lower() not in sheet.lower(), (
            f"worksheet leaks machine output: {leak!r}"
        )
    # it must render with the sensor package unimportable
    probe = (
        "import sys, os\n"
        f"sys.path.insert(0, {REPO_ROOT!r})\n"
        "import practice.article_check as ac\n"
        "sys.modules['sensor_suite.sensors.conflict_diagnosis'] = None\n"
        "out = ac.blank_worksheet()\n"
        "assert 'STATED PROBLEM' in out\n"
        "print('ok')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe], capture_output=True, text=True, cwd=REPO_ROOT
    )
    assert result.returncode == 0, result.stderr
    print("  worksheet is result-free and renders without the sensors")
    print("  PASS")


# ----------------------------------------------------------------------
# Comparison arithmetic
# ----------------------------------------------------------------------

def test_tier_rank_ordering():
    print("[test_tier_rank_ordering]")
    ranks = [tier_rank(t) for t in TIER_LEVELS]
    assert ranks == sorted(ranks), "TIER_LEVELS is not in ascending severity"
    assert tier_rank("GREEN") < tier_rank("AMBER") < tier_rank("RED") < tier_rank("BLACK")
    try:
        tier_rank("MAUVE")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown tier ranked without error")
    print(f"  {' < '.join(TIER_LEVELS)}")
    print("  PASS")


def test_divergence_directions():
    print("[test_divergence_directions]")
    human = a_human_read(**{"Stated Problem": "RED", "Hidden Driver": "GREEN"})
    machine = a_machine_read(**{"Stated Problem": "GREEN", "Hidden Driver": "RED"})
    by_layer = {d.layer: d for d in compare(human, machine)}

    assert by_layer["Stated Problem"].kind == YOU_SAW_MORE
    assert by_layer["Hidden Driver"].kind == FERRET_SAW_MORE
    assert by_layer["Feasibility Gap"].kind == AGREE
    assert by_layer["Stated Problem"].distance == 2
    assert by_layer["Feasibility Gap"].distance == 0
    print("  all three directions classified correctly")
    print("  PASS")


def test_divergences_sorted_most_divergent_first():
    """The reader's attention is finite; the biggest gap goes on top."""
    print("[test_divergences_sorted_most_divergent_first]")
    human = a_human_read(**{"Consequence Analysis": "RED", "Feedback Loops": "AMBER"})
    divergences = compare(human, a_machine_read())
    distances = [d.distance for d in divergences]
    assert distances == sorted(distances, reverse=True), distances
    assert divergences[0].layer == "Consequence Analysis"
    print(f"  ordered by distance: {distances}")
    print("  PASS")


def test_every_layer_appears_exactly_once():
    print("[test_every_layer_appears_exactly_once]")
    divergences = compare(a_human_read(), a_machine_read())
    layers = [d.layer for d in divergences]
    assert sorted(layers) == sorted(LAYER_NAMES), layers
    assert len(layers) == len(set(layers))
    print(f"  {len(layers)} layers, no duplicates, none dropped")
    print("  PASS")


def test_agreement_is_not_reported_as_success():
    """Agreement with a keyword matcher is weak evidence, and the report
    must say so rather than congratulating the reader."""
    print("[test_agreement_is_not_reported_as_success]")
    report = format_report(a_human_read(), a_machine_read())
    lowered = report.lower()
    assert "not a grade" in lowered
    assert "weak evidence" in lowered
    for congratulation in ("correct", "well done", "accuracy", "you scored"):
        assert congratulation not in lowered, (
            f"report frames the comparison as a grade: {congratulation!r}"
        )
    print("  report refuses to grade")
    print("  PASS")


def test_report_surfaces_matched_phrases_when_ferret_saw_more():
    """Being told the ferret disagreed is useless without the evidence;
    the phrases are what let the reader adjudicate."""
    print("[test_report_surfaces_matched_phrases_when_ferret_saw_more]")
    machine = a_machine_read(**{"Hidden Driver": "RED"})
    machine.layer_hits["Hidden Driver"] = 11
    machine.layer_matches["Hidden Driver"] = ["Follow the money", "real reason"]
    report = format_report(a_human_read(), machine)
    assert "Follow the money" in report
    assert "real reason" in report
    assert "11 pattern hit" in report
    print("  matched phrases surfaced with hit count")
    print("  PASS")


def test_missing_falsifiability_answer_is_called_out():
    print("[test_missing_falsifiability_answer_is_called_out]")
    blank = a_human_read()
    blank.answers = {}
    report = format_report(blank, a_machine_read())
    assert "change your mind" in report.lower()
    assert "blank" in report.lower()
    print("  blank falsifiability answer flagged rather than ignored")
    print("  PASS")


# ----------------------------------------------------------------------
# Worksheet + end to end
# ----------------------------------------------------------------------

def test_worksheet_contains_every_question():
    print("[test_worksheet_contains_every_question]")
    sheet = blank_worksheet()
    for q in LAYER_QUESTIONS:
        assert q.layer.upper() in sheet, f"{q.layer} missing from worksheet"
    for q in OPEN_QUESTIONS:
        stem = " ".join(q.ask.split())[:40]
        assert stem in " ".join(sheet.split()), f"{q.key} missing from worksheet"
    assert sheet.count("Rating (GREEN / AMBER / RED)") == len(LAYER_QUESTIONS)
    print(f"  all {len(LAYER_QUESTIONS) + len(OPEN_QUESTIONS)} questions present")
    print("  PASS")


def test_worksheet_is_printable():
    """Wrapped to WIDTH so it prints on paper without reflowing."""
    print("[test_worksheet_is_printable]")
    sheet = blank_worksheet()
    long_lines = [l for l in sheet.split("\n") if len(l) > WIDTH]
    assert not long_lines, f"{len(long_lines)} line(s) exceed {WIDTH}: {long_lines[:2]}"
    assert sheet.isascii(), "worksheet contains non-ASCII"
    print(f"  every line <= {WIDTH} cols, pure ASCII")
    print("  PASS")


def test_end_to_end_against_the_example():
    """The documented invocation, on the file the repo ships."""
    print("[test_end_to_end_against_the_example]")
    assert os.path.exists(EXAMPLE), "examples/offshore_wind_radar.txt missing"
    text = open(EXAMPLE, encoding="utf-8").read()

    machine = machine_read(text)
    assert set(machine.layer_tiers) == set(LAYER_NAMES)
    assert machine.overall in TIER_LEVELS
    assert 0.0 <= machine.camouflage_score <= 1.0

    report = format_report(a_human_read(**{"Stated Problem": "RED"}), machine)
    assert "ARTICLE CHECK" in report
    assert "CALIBRATION READOUT" in report
    for name in LAYER_NAMES:
        assert name in report, f"{name} missing from report"
    print(f"  ferret tier {machine.overall}, camouflage "
          f"{machine.camouflage_score:.2f}; all 8 layers reported")
    print("  PASS")


def test_runner_replays_a_saved_read():
    """The --answers path, so a read done on paper can be entered later
    without the runner prompting (and without stdin in CI)."""
    print("[test_runner_replays_a_saved_read]")
    import tempfile

    read = {
        "overall": "AMBER",
        "layers": {name: "AMBER" for name in LAYER_NAMES},
        "answers": {"falsifiable": "A published cost breakdown."},
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(read, fh)
        path = fh.name
    try:
        result = subprocess.run(
            [sys.executable, "run_article_check.py", EXAMPLE, "--answers", path],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        assert result.returncode == 0, result.stderr
        assert "CALIBRATION READOUT" in result.stdout
        assert "A published cost breakdown." in result.stdout
    finally:
        os.unlink(path)
    print("  saved read replayed without prompting")
    print("  PASS")


def test_runner_rejects_incomplete_saved_read():
    print("[test_runner_rejects_incomplete_saved_read]")
    import tempfile

    read = {"overall": "AMBER", "layers": {"Stated Problem": "RED"}}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(read, fh)
        path = fh.name
    try:
        result = subprocess.run(
            [sys.executable, "run_article_check.py", EXAMPLE, "--answers", path],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        assert result.returncode != 0, "incomplete read was accepted"
        assert "Incomplete read" in result.stdout
        assert "CALIBRATION" not in result.stdout, (
            "a report was produced from an incomplete read"
        )
    finally:
        os.unlink(path)
    print("  incomplete saved read rejected before any machine output")
    print("  PASS")


def test_worksheet_runner_flag():
    print("[test_worksheet_runner_flag]")
    result = subprocess.run(
        [sys.executable, "run_article_check.py", "--worksheet"],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert "ARTICLE CHECK -- WORKSHEET" in result.stdout
    print("  --worksheet prints the blank sheet")
    print("  PASS")


if __name__ == "__main__":
    test_one_question_per_diagnosis_layer()
    test_every_question_is_substantive()
    test_prior_belief_is_asked_first()
    test_falsifiability_question_present()
    test_rating_scale_matches_tier_levels()
    test_report_requires_complete_read()
    test_black_rejected_per_layer()
    test_machine_read_not_reachable_from_worksheet()
    test_tier_rank_ordering()
    test_divergence_directions()
    test_divergences_sorted_most_divergent_first()
    test_every_layer_appears_exactly_once()
    test_agreement_is_not_reported_as_success()
    test_report_surfaces_matched_phrases_when_ferret_saw_more()
    test_missing_falsifiability_answer_is_called_out()
    test_worksheet_contains_every_question()
    test_worksheet_is_printable()
    test_end_to_end_against_the_example()
    test_runner_replays_a_saved_read()
    test_runner_rejects_incomplete_saved_read()
    test_worksheet_runner_flag()
    print("\nall article check tests passed.")
