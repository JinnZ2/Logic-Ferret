"""
Tests for informational_cost_audit -- the companion reasoning
artifact on the cost spiral of maintaining false certainty.

Pure data module; no functions to test. These are STRUCTURAL
tests: the public constants must exist, be the expected types,
and contain the expected key paths so downstream consumers can
iterate them safely. We do NOT test content correctness -- this
is a reasoning artifact, not a formal model.

Run directly:
    python tests/test_informational_cost_audit.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge import informational_cost_audit as ica


def test_module_importable():
    print("[test_module_importable]")
    assert hasattr(ica, "__all__")
    # public surface is declared
    assert len(ica.__all__) == 9
    print(f"  __all__ declares {len(ica.__all__)} public names")
    print("  PASS")


def test_geocentric_comfort_state_shape():
    print("[test_geocentric_comfort_state_shape]")
    gcs = ica.GEOCENTRIC_COMFORT_STATE
    assert isinstance(gcs, dict)
    assert "what_people_believed" in gcs
    assert "why_it_was_comfortable" in gcs
    assert "informational_cost_of_commitment" in gcs
    assert isinstance(gcs["why_it_was_comfortable"], list)
    assert len(gcs["why_it_was_comfortable"]) >= 3
    print(f"  {len(gcs['why_it_was_comfortable'])} comfort reasons enumerated")
    print("  PASS")


def test_anomalies_has_four_cases():
    print("[test_anomalies_has_four_cases]")
    a = ica.ANOMALIES_UNDER_GEOCENTRISM
    expected = {
        "retrograde_motion_of_planets",
        "venus_phases",
        "stellar_parallax",
        "moons_of_jupiter",
    }
    assert set(a.keys()) == expected, f"missing: {expected - set(a.keys())}"
    # each case must carry observation / problem / solution / cost
    for name, entry in a.items():
        required = {"observation", "geocentric_problem", "geocentric_solution", "cost"}
        missing = required - set(entry.keys())
        assert not missing, f"{name} missing {missing}"
    print("  all 4 anomaly cases carry the 4 required fields")
    print("  PASS")


def test_cost_accumulation_stages_in_order():
    print("[test_cost_accumulation_stages_in_order]")
    stages = list(ica.INFORMATION_COST_ACCUMULATION.keys())
    # stages are numbered explicitly; must appear in order
    assert stages == [
        "stage_1_comfort",
        "stage_2_first_anomaly",
        "stage_3_more_anomalies",
        "stage_4_system_collapse",
    ]
    # each stage names an entropy level or cost description
    for name, stage in ica.INFORMATION_COST_ACCUMULATION.items():
        assert isinstance(stage, dict)
        assert "state" in stage, f"{name} missing 'state'"
    print("  4 stages in declared order; each has a 'state' entry")
    print("  PASS")


def test_heliocentric_uncertainty_state_shape():
    print("[test_heliocentric_uncertainty_state_shape]")
    h = ica.HELIOCENTRIC_UNCERTAINTY_STATE
    assert "what_copernicus_had" in h
    assert "why_it_was_uncomfortable" in h
    assert "informational_cost_of_uncertainty" in h
    assert "what_happens_when_instruments_improve" in h
    wh = h["what_happens_when_instruments_improve"]
    # stages_1/2/3 plus cost + gain
    assert "stage_1" in wh
    assert "stage_2" in wh
    assert "stage_3" in wh
    assert "cost" in wh
    assert "gain" in wh
    print("  3 instrument-improvement stages + cost + gain present")
    print("  PASS")


def test_comparison_audit_has_both_paths():
    """The core comparison: geocentrism vs heliocentrism. Both
    paths must be defined with the expected cost fields."""
    print("[test_comparison_audit_has_both_paths]")
    ia = ica.INFORMATION_COST_AUDIT
    assert set(ia.keys()) == {"geocentrism_path", "heliocentrism_path"}

    geo = ia["geocentrism_path"]
    helio = ia["heliocentrism_path"]

    for path_name, path in [("geocentrism", geo), ("heliocentrism", helio)]:
        assert "total_cost_accumulated" in path, f"{path_name}: missing total"
        assert "cost_when_regime_shifts" in path, f"{path_name}: missing regime cost"
        assert "final_verdict" in path, f"{path_name}: missing verdict"
    print("  both paths carry total/regime/verdict fields")
    print("  PASS")


def test_information_theory_insight_four_claims():
    """The deeper principle section enumerates four
    distinct claims about apparent vs. actual entropy."""
    print("[test_information_theory_insight_four_claims]")
    it = ica.INFORMATION_THEORY_INSIGHT
    assert set(it.keys()) == {
        "shannon_entropy",
        "but_the_reality",
        "the_paradox",
        "compression_insight",
    }
    for name, s in it.items():
        assert isinstance(s, str), f"{name}: not a string"
        assert len(s) > 50, f"{name}: suspiciously short"
    print("  4 information-theory claims, all substantive")
    print("  PASS")


def test_ai_implications_calls_out_the_question():
    """AI_IMPLICATIONS is the operative section for systems
    consuming this artifact. Must explicitly name the
    comfort-vs-resilience tradeoff."""
    print("[test_ai_implications_calls_out_the_question]")
    ai = ica.AI_IMPLICATIONS
    assert "current_AI_behavior" in ai
    assert "what_uncertainty_looks_like_instead" in ai
    assert "the_real_question_for_AI" in ai
    q = ai["the_real_question_for_AI"]
    # naming the tradeoff is load-bearing for the artifact
    assert "comfort" in q.lower() and "resilience" in q.lower()
    print("  the comfort-vs-resilience question is explicitly named")
    print("  PASS")


def test_historical_pattern_names_the_cycle():
    print("[test_historical_pattern_names_the_cycle]")
    hp = ica.HISTORICAL_PATTERN
    assert "what_always_happens" in hp
    assert "what_rarely_happens" in hp
    assert "why_it_rarely_happens" in hp
    cycle = hp["what_always_happens"]
    assert isinstance(cycle, list)
    # cycle must be long enough to actually describe the pattern
    assert len(cycle) >= 7
    # "cycle repeats" is the closing note of a real cycle
    assert any("cycle repeats" in step.lower() for step in cycle)
    print(f"  cycle has {len(cycle)} steps and closes with 'cycle repeats'")
    print("  PASS")


def test_verdict_has_one_liner():
    """The VERDICT section ends with a one-liner intended to be
    quotable / directly cited by downstream consumers."""
    print("[test_verdict_has_one_liner]")
    v = ica.VERDICT
    assert v["comfort_is_expensive"] is True
    assert v["uncertainty_is_cheap"] is True
    assert "one_liner" in v
    oneliner = v["one_liner"]
    assert isinstance(oneliner, str)
    # genuine one-liner: no newlines
    assert "\n" not in oneliner
    assert len(oneliner) > 30
    print(f"  one_liner: {oneliner!r}")
    print("  PASS")


def test_verdict_for_ai_and_for_humans_both_present():
    print("[test_verdict_for_ai_and_for_humans_both_present]")
    v = ica.VERDICT
    assert "for_AI" in v
    assert "for_humans" in v
    assert isinstance(v["for_AI"], str) and len(v["for_AI"]) > 50
    assert isinstance(v["for_humans"], str) and len(v["for_humans"]) > 50
    print("  both audience-specific verdicts present")
    print("  PASS")


def test_reexported_via_package_root():
    """All public constants must be reachable via `from
    logic_ferret import ...`. VERDICT is aliased to
    INFORMATIONAL_COST_VERDICT at package scope to avoid a
    generic name collision."""
    print("[test_reexported_via_package_root]")
    import sys as _sys, importlib.util as _util, os as _os
    repo_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    spec = _util.spec_from_file_location(
        "logic_ferret",
        _os.path.join(repo_root, "__init__.py"),
        submodule_search_locations=[repo_root],
    )
    pkg = _util.module_from_spec(spec)
    _sys.modules["logic_ferret"] = pkg
    spec.loader.exec_module(pkg)
    for name in [
        "GEOCENTRIC_COMFORT_STATE",
        "ANOMALIES_UNDER_GEOCENTRISM",
        "INFORMATION_COST_ACCUMULATION",
        "HELIOCENTRIC_UNCERTAINTY_STATE",
        "INFORMATION_COST_AUDIT",
        "INFORMATION_THEORY_INSIGHT",
        "AI_IMPLICATIONS",
        "HISTORICAL_PATTERN",
        "INFORMATIONAL_COST_VERDICT",
    ]:
        assert hasattr(pkg, name), f"{name} not re-exported"
    # The spec loader re-imports the submodule under the logic_ferret.*
    # namespace, so identity fails even though content matches. Compare
    # by value to verify the alias exposes the same data.
    assert pkg.INFORMATIONAL_COST_VERDICT == ica.VERDICT
    assert "one_liner" in pkg.INFORMATIONAL_COST_VERDICT
    print("  all 9 names reachable; VERDICT alias verified")
    print("  PASS")


if __name__ == "__main__":
    test_module_importable()
    test_geocentric_comfort_state_shape()
    test_anomalies_has_four_cases()
    test_cost_accumulation_stages_in_order()
    test_heliocentric_uncertainty_state_shape()
    test_comparison_audit_has_both_paths()
    test_information_theory_insight_four_claims()
    test_ai_implications_calls_out_the_question()
    test_historical_pattern_names_the_cycle()
    test_verdict_has_one_liner()
    test_verdict_for_ai_and_for_humans_both_present()
    test_reexported_via_package_root()
    print("\nall informational_cost_audit tests passed.")
