# /sensors/truth_integrity_score.py

from typing import Dict, Tuple

# Sensor weights for the composite Truth Integrity Score (C3).
# Higher weight = stronger contribution per unit score.
#
# "Discourse Collapse" carries the highest weight (2.0) because it's
# the only sensor whose full-score emission corresponds to BLACK tier
# -- collapse of the reasoning apparatus itself, qualitatively worse
# than camouflage. The other sensors cap at RED by design.
#
# Note on dilution: C3 averages weighted scores and normalizes by
# weight_sum. A lone BLACK discourse signal with all other sensors
# quiet still reads ~0.12 after normalization. This is intentional:
# C3 is a *composite* integrity signal, not a tier readout. For
# tier routing, consume diagnose()["tier"] directly. For a per-
# sensor tier vector, use schema_contract.sensor_tiers().
_WEIGHTS = {
    "Propaganda Tone":     1.2,
    "Reward Manipulation": 1.0,
    "False Urgency":       1.1,
    "Gatekeeping":         1.3,
    "Narrative Fragility": 1.4,
    "Propaganda Bias":     1.5,
    "Agency Score":        1.6,
    "Discourse Collapse":  2.0,
}

# Note 2026-11-20: sensors where a higher score is the good direction. Their scores are
# inverted before weighting, so that more accountability lowers C3 instead of raising it.
# Until this change every score was added as-is. Names are the keys used in
# run_full_sensor_scan.SENSORS on main. Ported from a5ff55b
# (claude/add-claude-documentation-4a69p), which used the key "Meritocracy".
POSITIVE_SENSORS = {"True Accountability", "Meritocracy Detector"}


def void_positive_sensors(flags_by_sensor: Dict[str, dict]) -> set:
    """
    Names of positive sensors that matched nothing in the text.

    Note 2026-11-20 (second branch of the inversion change): a positive sensor whose
    count flags are all zero has measured nothing. Inverting its 0.0 to 1.0 would read
    "no accountability phrases found" as "full distortion". Such a sensor is VOID: it is
    left out of the sum and out of the weight total.

    A positive sensor that scores 0.0 because its negative counts outweigh its positive
    ones has measured something and is not VOID. That is why this reads the count flags
    and not the score.
    """
    void = set()
    for name in POSITIVE_SENSORS:
        flags = flags_by_sensor.get(name)
        if flags is None:
            continue
        counts = [v for v in flags.values() if isinstance(v, int) and not isinstance(v, bool)]
        if counts and sum(counts) == 0:
            void.add(name)
    return void


def calculate_c3(sensor_scores: Dict[str, float], void=()) -> Tuple[float, Dict[str, float]]:
    weights = _WEIGHTS

    weighted_total = 0
    weight_sum = 0

    debug_weights = {}

    for name, score in sensor_scores.items():
        if name in void:
            # VOID: not measured. No contribution and no weight; the remaining
            # sensors are renormalized by their own weight total.
            continue
        w = weights.get(name, 1.0)
        effective = (1.0 - score) if name in POSITIVE_SENSORS else score
        weighted_total += effective * w
        weight_sum += w
        debug_weights[name] = round(effective * w, 3)

    # Note 2026-11-20: was `min(weighted_total / weight_sum, 1.0)`, which raised
    # ZeroDivisionError on an empty dict. No scores now gives 0.0.
    c3_score = min(weighted_total / weight_sum, 1.0) if weight_sum else 0.0

    return c3_score, debug_weights
