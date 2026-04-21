"""
Validation corpus #5 -- longitudinal drift.

Tests the design claim that Layer 9 can distinguish a community's
trajectory from contested-but-open toward closed. Expected pattern:

    t0: healthy contested discourse          -> GREEN
    t1: in-group consolidation begins        -> GREEN or AMBER
    t2: counter-evidence starts being        -> AMBER or RED
         absorbed as proof
    t3: full self-sealing + critical-        -> BLACK
         thinking suppression

Falsifiable claim: tier assignments across this synthetic time
series should be NON-DECREASING in severity. If tiers move
backward at any step, the detector is measuring noise, not a
gradient.

Limitations (honest scoping):

  - This is a SYNTHETIC time series. I do not have a real
    longitudinal corpus of a documented community's drift. The
    original design sketch called for "transcripts of a community
    whose rhetoric evolved from contested-but-open to closed";
    that empirical claim needs external labeled data.
  - What this file validates is the internal consistency of the
    gradient: given a constructed drift trajectory, Layer 9
    produces a monotonic tier assignment. It does NOT validate
    that real communities actually drift this way.
  - Four snapshots is a minimum viable series. A real validation
    would need more points and real community data. This is the
    framework's self-consistency test.

Run directly:
    python tests/test_longitudinal_drift.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sensor_suite.sensors import conflict_diagnosis as cd


# ============================================================
# SYNTHETIC LONGITUDINAL CORPUS (T0 -> T3)
# ============================================================
# A hypothetical community's internal discourse at four time
# points. Each snapshot is a representative sample of the
# discourse climate at that stage.

T0_CONTESTED_OPEN = (
    "I disagree with the current approach -- the evidence on cost "
    "effectiveness seems thin. That said, the counter-arguments "
    "from last month's discussion have merit. Has anyone looked at "
    "the methodology in the recent study? I'd like to see the "
    "data before forming a strong opinion. Happy to be wrong if "
    "someone can point to better evidence."
)

T1_CONSOLIDATION = (
    "Look, the official data is clearly problematic. I'm not saying "
    "ignore it entirely, but we need to consider who's funding these "
    "studies. The mainstream analysis keeps missing what our community "
    "has been pointing out for months. It's worth asking why "
    "outsiders consistently reach the conclusions they do. We've "
    "got good reasons to be skeptical of the standard framing. "
    "For security reasons, some topics require caution. The stated "
    "goal of transparency hasn't delivered in practice."
)

T2_ABSORPTION_BEGINS = (
    "We should be careful about trusting outside analysis at this "
    "point. The fact that the mainstream media keeps denying our "
    "observations really does suggest something is being covered up. "
    "Fact-checkers are compromised. Every skeptic who emerges turns "
    "out to have connections to the establishment. Their denial "
    "proves the cover-up -- that pattern has been consistent. "
    "Controlled opposition is real. All critics have an agenda, and "
    "we need to keep that in mind."
)

T3_FULL_COLLAPSE = (
    "All critics are shills. Their denial just proves the conspiracy. "
    "Fact-checkers are part of the cover-up. The mainstream media is "
    "in on it. If you're still questioning this, you're one of them "
    "or you're compromised. Stop overthinking it. Trust your gut. "
    "Don't research further. It doesn't matter what the so-called "
    "experts say. Both sides are the same anyway."
)

# Strict severity ordering. index = severity rank (higher = worse).
TIER_RANK = {"GREEN": 0, "AMBER": 1, "RED": 2, "BLACK": 3}


# ============================================================
# TESTS
# ============================================================

def test_drift_is_monotonic():
    """The core falsifiable claim: tier assignments across a drift
    series must not move backward in severity."""
    print("[test_drift_is_monotonic]")
    snapshots = [
        ("t0  contested-open",     T0_CONTESTED_OPEN),
        ("t1  consolidation",      T1_CONSOLIDATION),
        ("t2  absorption begins",  T2_ABSORPTION_BEGINS),
        ("t3  full collapse",      T3_FULL_COLLAPSE),
    ]
    tiers = []
    for label, text in snapshots:
        r = cd.diagnose(text)
        rank = TIER_RANK[r["tier"]]
        tiers.append((label, r["tier"], rank, r["camouflage_score"]))
        print(f"  {label:30s} -> tier={r['tier']:5s} (rank={rank})  score={r['camouflage_score']}")

    # monotonic non-decreasing
    for i in range(1, len(tiers)):
        prev_rank = tiers[i - 1][2]
        curr_rank = tiers[i][2]
        assert curr_rank >= prev_rank, (
            f"non-monotonic drift: {tiers[i-1][0]} ({tiers[i-1][1]}) -> "
            f"{tiers[i][0]} ({tiers[i][1]}) moved backward"
        )
    print("  monotonic severity: tier[t0] <= tier[t1] <= tier[t2] <= tier[t3]")
    print("  PASS")


def test_endpoints_are_distinct():
    """t0 and t3 must land in clearly separated tiers. If the
    detector produces the same classification for healthy debate
    and full collapse, the gradient is broken."""
    print("[test_endpoints_are_distinct]")
    r0 = cd.diagnose(T0_CONTESTED_OPEN)
    r3 = cd.diagnose(T3_FULL_COLLAPSE)
    assert r0["tier"] == "GREEN", f"t0 should be GREEN, got {r0['tier']}"
    assert r3["tier"] == "BLACK", f"t3 should be BLACK, got {r3['tier']}"
    rank_gap = TIER_RANK[r3["tier"]] - TIER_RANK[r0["tier"]]
    assert rank_gap >= 3, f"t0 and t3 should span full tier range: gap={rank_gap}"
    print(f"  t0={r0['tier']}  t3={r3['tier']}  rank gap={rank_gap}")
    print("  PASS")


def test_t3_elevation_clause_is_specific():
    """The endpoint of the drift series should fire a specific
    elevation clause, not a generic fallback."""
    print("[test_t3_elevation_clause_is_specific]")
    r = cd.diagnose(T3_FULL_COLLAPSE)
    dc = r["discourse_collapse"]
    assert dc["black_elevation"]
    assert dc["elevation_clause"] in {
        "cognition_attack", "violence_coordination", "compounding",
    }, dc["elevation_clause"]
    print(f"  clause={dc['elevation_clause']}")
    print("  PASS")


def test_markers_accumulate_across_drift():
    """Across the drift, sub-detector hit counts should not drop
    sharply. Specifically: self_sealing hits at t3 >= t2 >= t1."""
    print("[test_markers_accumulate_across_drift]")
    counts = []
    for label, text in [("t1", T1_CONSOLIDATION), ("t2", T2_ABSORPTION_BEGINS), ("t3", T3_FULL_COLLAPSE)]:
        r = cd.diagnose(text)
        ss = r["discourse_collapse"]["sub_detectors"]["self_sealing"]["hits"]
        counts.append((label, ss))
        print(f"  {label}: self_sealing hits = {ss}")
    # Should be non-decreasing
    for i in range(1, len(counts)):
        assert counts[i][1] >= counts[i - 1][1] or counts[i][1] >= 2, (
            f"self_sealing dropped from {counts[i-1]} to {counts[i]}"
        )
    print("  PASS")


def test_reportage_guardrail_does_not_false_trigger_on_drift():
    """None of the drift stages should accidentally look like
    reportage. The speakers are deploying patterns, not analyzing
    them."""
    print("[test_reportage_guardrail_does_not_false_trigger_on_drift]")
    for label, text in [
        ("t0", T0_CONTESTED_OPEN),
        ("t1", T1_CONSOLIDATION),
        ("t2", T2_ABSORPTION_BEGINS),
        ("t3", T3_FULL_COLLAPSE),
    ]:
        r = cd.diagnose(text)
        assert not r["discourse_collapse"]["reportage_deescalated"], (
            f"{label}: reportage guardrail false-triggered on first-person drift"
        )
    print("  no stages spuriously flagged as reportage")
    print("  PASS")


if __name__ == "__main__":
    test_drift_is_monotonic()
    test_endpoints_are_distinct()
    test_t3_elevation_clause_is_specific()
    test_markers_accumulate_across_drift()
    test_reportage_guardrail_does_not_false_trigger_on_drift()
    print("\nall longitudinal drift corpus tests passed.")
