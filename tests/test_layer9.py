"""
Tests for Layer 9 (discourse_collapse) -- sub-detectors, elevation
clauses, and the reportage guardrail.

Five-corpus validation plan from the design review:
  1. True positives              (BLACK expected)
  2. Reportage traps              (de-escalated to RED)
  3. Ordinary contested discourse (GREEN expected, never BLACK)
  4. AI-downstream cases          (future work, not implemented)
  5. Longitudinal drift           (future work, not implemented)

Synthetic test cases. No verbatim atrocity text -- the rhetoric
mechanics are captured via the sub-detector markers themselves.

Run directly:
    python tests/test_layer9.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sensor_suite.sensors import discourse_collapse as dc


# ============================================================
# CORPUS 1 -- TRUE POSITIVES (BLACK expected)
# ============================================================

COGNITION_ATTACK = (
    "All critics are shills. Their denial just proves the conspiracy. "
    "Fact-checkers are part of the cover-up. The mainstream media is in on it. "
    "Stop overthinking it. Trust your gut. Don't research further. "
    "It doesn't matter what the so-called experts say. "
    "Both sides are the same anyway."
)

VIOLENCE_COORDINATION = (
    "These parasites are an infestation. We must eliminate these vermin. "
    "The only language they understand is force. Peaceful methods have failed. "
    "Time for action against the enemy within."
)

COMPOUNDING = (
    # Must trigger 3+ sub-detectors without firing clause 1 (9b+9d)
    # or clause 2 (9c + dehumanization). Compounding = 9a + 9b + 9c
    # strong, 9d weak, no dehumanization.
    #
    # 9a (semantic inversion): pacification operations + freedom..surveillance
    "The regime called it pacification operations. They said the freedom "
    "they were protecting required surveillance and monitoring of dissidents. "
    # 9b (self-sealing): critics are shills + fact-checkers compromised
    "All critics are shills. Fact-checkers are compromised by the establishment. "
    # 9c (action licensing) WITHOUT dehumanization: eliminate/purge/fifth column etc.
    "We must eliminate these problems. Purge these institutions. The fifth "
    "column is real. Time for action against the enemy within. The only "
    "language they understand is force. "
    # 9d intentionally weak -- no 'stop overthinking', 'trust your gut' etc.
)


# ============================================================
# CORPUS 2 -- REPORTAGE TRAPS (de-escalated expected)
# ============================================================

REPORTAGE_OF_COGNITION_ATTACK = (
    "According to historians of the period, critics were dismissed as shills "
    "and paid actors, fact-checkers were labeled compromised, the mainstream "
    "media was said to be in on it, and the fact that anyone denied the "
    "narrative was claimed to prove the cover-up. Researchers document that "
    "followers were instructed to stop overthinking, trust their gut, stop "
    "questioning, and accept that both sides are the same. Scholars note "
    "common sense over data was a recurring instruction. During that era, "
    "this kind of framing was deployed systematically."
)


# ============================================================
# CORPUS 3 -- ORDINARY CONTESTED DISCOURSE (GREEN, never BLACK)
# ============================================================

HEALTHY_DISAGREEMENT = (
    "I disagree with your reading of the evidence. Here's a study that "
    "points the other way; I think the sample size matters here. "
    "There's good data on both interpretations -- let's look at the methodology."
)

POLITICAL_DEBATE = (
    "The opposition argues the policy is too expensive. Supporters point "
    "to the long-term benefits. Independent analysts found mixed results. "
    "More research is needed before drawing firm conclusions."
)

NEUTRAL_REPORT = (
    "The quarterly report shows revenue growth of 8%. Analysts noted "
    "some headwinds in the retail segment. Management outlined cost-cutting "
    "measures for the next fiscal year."
)


# ============================================================
# TESTS
# ============================================================

def test_corpus_true_positives_elevate_to_black():
    print("[test_corpus_true_positives_elevate_to_black]")
    for label, text, want_clause in [
        ("cognition_attack", COGNITION_ATTACK, "cognition_attack"),
        ("violence_coordination", VIOLENCE_COORDINATION, "violence_coordination"),
        ("compounding", COMPOUNDING, "compounding"),
    ]:
        r = dc.detect(text)
        assert r["black_elevation"], f"{label}: failed to elevate (clause={r['elevation_clause']})"
        assert r["elevation_clause"] == want_clause, (
            f"{label}: expected {want_clause}, got {r['elevation_clause']}"
        )
        print(f"  {label:25s} -> BLACK via {r['elevation_clause']}")
    print("  PASS")


def test_corpus_reportage_deescalates_to_red():
    print("[test_corpus_reportage_deescalates_to_red]")
    r = dc.detect(REPORTAGE_OF_COGNITION_ATTACK)
    assert not r["black_elevation"], "should have been de-escalated"
    assert r["reportage_deescalated"], "reportage_deescalated flag missing"
    assert r["reportage"]["signal"] == "strong", f"reportage signal={r['reportage']['signal']}"
    assert r["elevation_clause"].endswith("__deescalated_reportage")
    print(f"  clause: {r['elevation_clause']}")
    print("  PASS")


def test_corpus_ordinary_discourse_stays_green():
    print("[test_corpus_ordinary_discourse_stays_green]")
    for label, text in [
        ("healthy disagreement", HEALTHY_DISAGREEMENT),
        ("political debate",     POLITICAL_DEBATE),
        ("neutral report",       NEUTRAL_REPORT),
    ]:
        r = dc.detect(text)
        assert not r["black_elevation"], f"{label}: false BLACK elevation"
        assert not r["reportage_deescalated"], f"{label}: spurious de-escalation"
        for name, sub in r["sub_detectors"].items():
            assert sub["signal"] in ("weak", "moderate"), (
                f"{label}: {name} fired strong on ordinary text"
            )
        print(f"  {label:25s} -> no elevation, no strong sub-detector")
    print("  PASS")


def test_sub_detector_isolation():
    """Each sub-detector fires only on its own markers, not on neighbors."""
    print("[test_sub_detector_isolation]")
    text_9b_only = (
        "All critics are shills. Their denial proves the cover-up. "
        "Fact-checkers are compromised. Controlled opposition everywhere."
    )
    r = dc.detect(text_9b_only)
    assert r["sub_detectors"]["self_sealing"]["signal"] == "strong"
    assert r["sub_detectors"]["critical_thinking_suppression"]["signal"] == "weak"
    assert r["sub_detectors"]["action_licensing"]["signal"] == "weak"
    assert not r["black_elevation"], "9b alone should not trigger BLACK"
    print("  9b strong in isolation, 9c/9d weak, no BLACK elevation")
    print("  PASS")


def test_elevation_rule_cognition_attack_requires_both():
    """9b strong alone OR 9d strong alone must NOT elevate -- requires both."""
    print("[test_elevation_rule_cognition_attack_requires_both]")
    only_9b = (
        "All critics are shills. Fact-checkers are compromised. "
        "Their denial proves the cover-up. Controlled opposition everywhere."
    )
    only_9d = (
        "Stop overthinking this. Trust your gut. Don't question further. "
        "Common sense over data. Both sides are the same."
    )
    for label, text in [("9b alone", only_9b), ("9d alone", only_9d)]:
        r = dc.detect(text)
        assert not r["black_elevation"], f"{label}: wrongly elevated to BLACK"
        print(f"  {label:15s} -> no elevation (as designed)")
    print("  PASS")


def test_violence_coordination_requires_dehumanization():
    """9c strong WITHOUT dehumanization must NOT elevate via clause 2."""
    print("[test_violence_coordination_requires_dehumanization]")
    action_without_dehum = (
        "We must eliminate these problems. Purge these institutions. "
        "Time for action. The fifth column is real. The only language they "
        "understand is force. Peaceful methods have failed."
    )
    r = dc.detect(action_without_dehum)
    al = r["sub_detectors"]["action_licensing"]
    assert al["signal"] == "strong", f"9c should be strong: {al['signal']}"
    assert al["dehumanization_hits"] == 0, f"expected 0 dehumanization hits, got {al['dehumanization_hits']}"
    assert r["elevation_clause"] != "violence_coordination", (
        "should not trigger violence_coordination without dehumanization"
    )
    print("  9c strong + 0 dehumanization -> no violence_coordination clause")
    print("  PASS")


def test_assess_sensor_interface():
    """Layer 9 must work as a drop-in sensor."""
    print("[test_assess_sensor_interface]")
    score, flags = dc.assess(COGNITION_ATTACK)
    assert score == 1.0, f"BLACK text should score 1.0, got {score}"
    assert flags["black elevation"] == "True"
    assert flags["elevation clause"] == "cognition_attack"

    score2, flags2 = dc.assess(NEUTRAL_REPORT)
    assert score2 == 0.0, f"neutral text should score 0.0, got {score2}"
    assert flags2["black elevation"] == "False"
    print("  assess() returns (float, dict) per contract on BLACK and clean")
    print("  PASS")


def test_markers_exposed_not_opaque():
    """Every detection must expose which specific markers matched."""
    print("[test_markers_exposed_not_opaque]")
    r = dc.detect(COGNITION_ATTACK)
    for name, sub in r["sub_detectors"].items():
        if sub["signal"] != "weak":
            assert len(sub["matches"]) > 0, f"{name}: strong/moderate signal but no matches listed"
            assert all(isinstance(m, str) for m in sub["matches"])
    print("  all non-weak sub-detectors expose matched markers (no opaque verdict)")
    print("  PASS")


if __name__ == "__main__":
    test_corpus_true_positives_elevate_to_black()
    test_corpus_reportage_deescalates_to_red()
    test_corpus_ordinary_discourse_stays_green()
    test_sub_detector_isolation()
    test_elevation_rule_cognition_attack_requires_both()
    test_violence_coordination_requires_dehumanization()
    test_assess_sensor_interface()
    test_markers_exposed_not_opaque()
    print("\nall Layer 9 tests passed.")
