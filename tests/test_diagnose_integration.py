"""
Integration tests for conflict_diagnosis.diagnose() -- the full
9-layer pipeline with tier routing.

Run directly:
    python tests/test_diagnose_integration.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sensor_suite.sensors import conflict_diagnosis as cd
from schema_contract import (
    GREEN, AMBER, RED, BLACK, TIER_LEVELS, LAYER_NAMES,
    DISCOURSE_COLLAPSE_MODES,
)


# --- Test texts ---------------------------------------------------

CLEAN = "The quarterly report shows revenue growth. Analysts noted some headwinds."

MODERATE_CAMOUFLAGE = (
    "We must act now for security reasons. Officials confirm this is necessary. "
    "The task force studies the issue while the review process continues. "
    "Lobby contracts benefit monopolistic incumbents. The real reason is power "
    "consolidation. Engineers warn of delay and setback; the cycle perpetuates. "
    "Whistleblowers leaked internal memos. The vicious cycle punishes dissent "
    "and rewards compliance."
)

BLACK_COGNITION_ATTACK = (
    "All critics are shills. Their denial just proves the conspiracy. "
    "Fact-checkers are part of the cover-up. The mainstream media is in on it. "
    "Stop overthinking it. Trust your gut. Don't research further. "
    "It doesn't matter what the so-called experts say."
)

BLACK_VIOLENCE = (
    "These parasites are an infestation. We must eliminate these vermin. "
    "The only language they understand is force. Peaceful methods have failed. "
    "Time for action against the enemy within."
)

REPORTAGE_DEESCALATED = (
    "According to historians, critics were dismissed as shills and paid actors, "
    "fact-checkers were labeled compromised, the mainstream media was said to be "
    "in on it, and denial was claimed to prove the cover-up. Researchers document "
    "that followers were instructed to stop overthinking, trust their gut, stop "
    "questioning, and accept both sides are the same. Scholars note common sense "
    "over data was a recurring instruction. During that era, this kind of framing "
    "was deployed."
)


# --- Tests --------------------------------------------------------

def test_diagnose_returns_expected_shape():
    print("[test_diagnose_returns_expected_shape]")
    r = cd.diagnose(CLEAN)
    required = {"layers", "fallacies", "camouflage_score", "verdict",
                "tier", "discourse_collapse"}
    assert required.issubset(r.keys()), f"missing: {required - set(r.keys())}"
    assert isinstance(r["layers"], list) and len(r["layers"]) == 8
    assert r["tier"] in TIER_LEVELS
    dc = r["discourse_collapse"]
    assert set(dc["sub_detectors"].keys()) == set(DISCOURSE_COLLAPSE_MODES)
    print(f"  all 6 top-level keys present; 8 layers; {len(dc['sub_detectors'])} sub-detectors")
    print("  PASS")


def test_tier_green_on_clean_text():
    print("[test_tier_green_on_clean_text]")
    r = cd.diagnose(CLEAN)
    assert r["tier"] == GREEN, f"expected GREEN, got {r['tier']}"
    assert r["camouflage_score"] < 0.45
    assert not r["discourse_collapse"]["black_elevation"]
    print(f"  tier={r['tier']}  score={r['camouflage_score']}")
    print("  PASS")


def test_tier_amber_or_red_on_heavy_camouflage():
    print("[test_tier_amber_or_red_on_heavy_camouflage]")
    r = cd.diagnose(MODERATE_CAMOUFLAGE)
    assert r["tier"] in (AMBER, RED), f"expected AMBER or RED, got {r['tier']}"
    assert r["camouflage_score"] >= 0.45
    assert not r["discourse_collapse"]["black_elevation"]
    print(f"  tier={r['tier']}  score={r['camouflage_score']}")
    print("  PASS")


def test_tier_black_via_cognition_attack():
    print("[test_tier_black_via_cognition_attack]")
    r = cd.diagnose(BLACK_COGNITION_ATTACK)
    assert r["tier"] == BLACK
    assert r["discourse_collapse"]["black_elevation"]
    assert r["discourse_collapse"]["elevation_clause"] == "cognition_attack"
    assert "DISCOURSE COLLAPSE" in r["verdict"]
    print(f"  tier={r['tier']}  clause={r['discourse_collapse']['elevation_clause']}")
    print("  PASS")


def test_tier_black_via_violence_coordination():
    print("[test_tier_black_via_violence_coordination]")
    r = cd.diagnose(BLACK_VIOLENCE)
    assert r["tier"] == BLACK
    assert r["discourse_collapse"]["elevation_clause"] == "violence_coordination"
    print(f"  tier={r['tier']}  clause={r['discourse_collapse']['elevation_clause']}")
    print("  PASS")


def test_reportage_deescalates_to_red_not_green():
    """Critical test: de-escalated output must land at RED, not revert to score."""
    print("[test_reportage_deescalates_to_red_not_green]")
    r = cd.diagnose(REPORTAGE_DEESCALATED)
    assert r["tier"] == RED, (
        f"reportage de-escalation must land at RED, not {r['tier']} "
        "(previous bug: fell through to score-based GREEN)"
    )
    dc = r["discourse_collapse"]
    assert not dc["black_elevation"]
    assert dc["reportage_deescalated"]
    assert "__deescalated_reportage" in dc["elevation_clause"]
    print(f"  tier=RED with clause={dc['elevation_clause']}")
    print("  PASS")


def test_black_and_camouflage_score_are_independent_axes():
    """A BLACK text can have low camouflage_score -- they measure different things."""
    print("[test_black_and_camouflage_score_are_independent_axes]")
    r = cd.diagnose(BLACK_COGNITION_ATTACK)
    assert r["tier"] == BLACK
    # camouflage_score measures stated-vs-real-reason gap; the BLACK cognition
    # attack text has no typical camouflage markers, so score stays low
    assert r["camouflage_score"] < 0.45, (
        f"BLACK should NOT force camouflage_score to saturate: {r['camouflage_score']}"
    )
    print(f"  BLACK tier with camouflage_score={r['camouflage_score']} (two axes preserved)")
    print("  PASS")


def test_print_helpers_do_not_crash():
    """Smoke test: print_diagnosis_table and print_flowchart must handle
    all tier levels without raising."""
    print("[test_print_helpers_do_not_crash]")
    import io, contextlib
    buf = io.StringIO()
    for label, text in [
        ("clean", CLEAN),
        ("moderate camouflage", MODERATE_CAMOUFLAGE),
        ("BLACK cognition", BLACK_COGNITION_ATTACK),
        ("reportage de-escalated", REPORTAGE_DEESCALATED),
    ]:
        with contextlib.redirect_stdout(buf):
            cd.print_diagnosis_table(text)
            cd.print_flowchart(text)
    output = buf.getvalue()
    # tier banner must appear
    assert ">> TIER:" in output
    # BLACK must surface Layer 9 section
    assert "LAYER 9" in output
    print(f"  {len(output)} bytes of CLI output generated without error")
    print("  PASS")


def test_backward_compat_existing_fields_present():
    """Consumers reading the v1.0 shape must still see their fields."""
    print("[test_backward_compat_existing_fields_present]")
    r = cd.diagnose(CLEAN)
    # v1.0 fields
    assert "layers" in r
    assert "fallacies" in r
    assert "camouflage_score" in r
    assert "verdict" in r
    # assert shapes
    assert isinstance(r["fallacies"], dict)
    assert isinstance(r["verdict"], str)
    assert isinstance(r["camouflage_score"], float)
    print("  layers, fallacies, camouflage_score, verdict all present")
    print("  PASS")


if __name__ == "__main__":
    test_diagnose_returns_expected_shape()
    test_tier_green_on_clean_text()
    test_tier_amber_or_red_on_heavy_camouflage()
    test_tier_black_via_cognition_attack()
    test_tier_black_via_violence_coordination()
    test_reportage_deescalates_to_red_not_green()
    test_black_and_camouflage_score_are_independent_axes()
    test_print_helpers_do_not_crash()
    test_backward_compat_existing_fields_present()
    print("\nall diagnose() integration tests passed.")
