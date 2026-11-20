"""
Before/after for three changes to the composite score (ported from a5ff55b):
  1. positive sensors are inverted before weighting
  2. an empty score dict gives 0.0 instead of ZeroDivisionError
  3. fallacy_overlay has assess(text)

"Before" is the formula main had until this change, copied here so the two can be
printed side by side.

Run directly:
    python tests/test_c3_inversion.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sensor_suite.sensors import truth_integrity_score as tis
from sensor_suite.sensors import fallacy_overlay


def c3_before(scores):
    """The formula on main before this change (no inversion, no guard)."""
    total = 0
    wsum = 0
    for name, score in scores.items():
        w = tis._WEIGHTS.get(name, 1.0)
        total += score * w
        wsum += w
    return min(total / wsum, 1.0)


QUIET = {
    "Propaganda Tone": 0.0, "Reward Manipulation": 0.0, "False Urgency": 0.0,
    "Gatekeeping": 0.0, "Narrative Fragility": 0.0, "Propaganda Bias": 0.0,
    "Agency Score": 0.0,
}


def test_accountability_lowers_c3():
    print("[test_accountability_lowers_c3]")
    low = dict(QUIET, **{"True Accountability": 0.0, "Meritocracy Detector": 0.0})
    high = dict(QUIET, **{"True Accountability": 1.0, "Meritocracy Detector": 1.0})
    b_low, b_high = c3_before(low), c3_before(high)
    a_low, _ = tis.calculate_c3(low)
    a_high, _ = tis.calculate_c3(high)
    print(f"  before: accountability 0.0 -> c3={b_low:.4f}   accountability 1.0 -> c3={b_high:.4f}")
    print(f"  after:  accountability 0.0 -> c3={a_low:.4f}   accountability 1.0 -> c3={a_high:.4f}")
    assert b_high > b_low      # before: more accountability raised the distortion score
    assert a_high < a_low      # after: more accountability lowers it
    assert a_high == 0.0
    print("  PASS")


def test_negative_sensors_unchanged():
    print("[test_negative_sensors_unchanged]")
    scores = {"Propaganda Tone": 0.5, "Gatekeeping": 0.8, "Discourse Collapse": 1.0}
    before = c3_before(scores)
    after, _ = tis.calculate_c3(scores)
    print(f"  before c3={before:.4f}  after c3={after:.4f}")
    assert before == after
    print("  PASS")


def test_empty_scores_give_zero():
    print("[test_empty_scores_give_zero]")
    try:
        c3_before({})
        before = "no error"
    except ZeroDivisionError:
        before = "ZeroDivisionError"
    after, br = tis.calculate_c3({})
    print(f"  before: {before}   after: c3={after}")
    assert before == "ZeroDivisionError"
    assert after == 0.0 and br == {}
    print("  PASS")


def test_fallacy_overlay_assess():
    print("[test_fallacy_overlay_assess]")
    text = "Everyone knows this. So what you're saying is we must choose? Obviously."
    score, counts = fallacy_overlay.assess(text)
    print(f"  score={score}  counts={counts}")
    assert 0.0 < score <= 1.0
    assert score == min(sum(counts.values()) / 10.0, 1.0)
    clean, _ = fallacy_overlay.assess("The pump moved 40 litres in ten minutes.")
    assert clean == 0.0
    print("  PASS")


if __name__ == "__main__":
    test_accountability_lowers_c3()
    test_negative_sensors_unchanged()
    test_empty_scores_give_zero()
    test_fallacy_overlay_assess()
    print("all c3 inversion tests passed.")
