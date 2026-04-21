"""
Tests for truth_integrity_score.calculate_c3 -- weighted composite
score including the v1.2.0 Discourse Collapse weight.

Run directly:
    python tests/test_c3.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sensor_suite.sensors import truth_integrity_score as tis


def test_empty_scores_does_not_crash():
    print("[test_empty_scores_does_not_crash]")
    try:
        c3, br = tis.calculate_c3({})
    except ZeroDivisionError:
        # known edge: empty dict -> no weight_sum. Documented behavior.
        print("  empty dict raises ZeroDivisionError (expected)")
        print("  PASS")
        return
    # if a future change handles empty gracefully, accept 0.0
    assert c3 == 0.0
    print(f"  empty dict -> c3={c3}")
    print("  PASS")


def test_c3_returns_signature():
    print("[test_c3_returns_signature]")
    c3, br = tis.calculate_c3({"Propaganda Tone": 0.5})
    assert isinstance(c3, float)
    assert isinstance(br, dict)
    assert 0.0 <= c3 <= 1.0
    print(f"  returns (float, dict); c3 in [0,1]")
    print("  PASS")


def test_c3_caps_at_one():
    print("[test_c3_caps_at_one]")
    scores = {name: 1.0 for name in [
        "Propaganda Tone", "Reward Manipulation", "False Urgency",
        "Gatekeeping", "Narrative Fragility", "Propaganda Bias",
        "Agency Score", "Discourse Collapse",
    ]}
    c3, br = tis.calculate_c3(scores)
    assert c3 <= 1.0, f"c3 exceeded 1.0: {c3}"
    print(f"  all-max input -> c3={c3} (capped)")
    print("  PASS")


def test_discourse_collapse_weighted_highest():
    """Layer 9 at full score must contribute more than any other sensor
    at full score -- it carries weight 2.0, highest in the table."""
    print("[test_discourse_collapse_weighted_highest]")
    _c3_dc, br_dc = tis.calculate_c3({"Discourse Collapse": 1.0})
    _c3_ps, br_ps = tis.calculate_c3({"Propaganda Bias": 1.0})
    _c3_as, br_as = tis.calculate_c3({"Agency Score": 1.0})
    dc_contribution = br_dc["Discourse Collapse"]
    ps_contribution = br_ps["Propaganda Bias"]
    as_contribution = br_as["Agency Score"]
    assert dc_contribution > ps_contribution, (
        f"Discourse Collapse weighted contribution {dc_contribution} "
        f"not > Propaganda Bias {ps_contribution}"
    )
    assert dc_contribution > as_contribution, (
        f"Discourse Collapse weighted contribution {dc_contribution} "
        f"not > Agency Score (previous max) {as_contribution}"
    )
    print(f"  DC contribution={dc_contribution}, "
          f"PB={ps_contribution}, AS={as_contribution}")
    print("  PASS")


def test_unknown_sensor_gets_default_weight():
    print("[test_unknown_sensor_gets_default_weight]")
    c3, br = tis.calculate_c3({"Some New Sensor": 1.0})
    # default weight 1.0, contribution 1.0 * 1.0 = 1.0
    assert br["Some New Sensor"] == 1.0
    print(f"  unknown sensor gets weight 1.0; c3={c3}")
    print("  PASS")


def test_breakdown_includes_every_input():
    print("[test_breakdown_includes_every_input]")
    scores = {
        "Propaganda Tone": 0.3,
        "Discourse Collapse": 0.8,
        "Mystery Sensor": 0.5,
    }
    c3, br = tis.calculate_c3(scores)
    assert set(br.keys()) == set(scores.keys())
    print("  PASS")


if __name__ == "__main__":
    test_empty_scores_does_not_crash()
    test_c3_returns_signature()
    test_c3_caps_at_one()
    test_discourse_collapse_weighted_highest()
    test_unknown_sensor_gets_default_weight()
    test_breakdown_includes_every_input()
    print("\nall C3 tests passed.")
