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

def calculate_c3(sensor_scores: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    weights = _WEIGHTS

    weighted_total = 0
    weight_sum = 0

    debug_weights = {}

    for name, score in sensor_scores.items():
        w = weights.get(name, 1.0)
        weighted_total += score * w
        weight_sum += w
        debug_weights[name] = round(score * w, 3)

    c3_score = min(weighted_total / weight_sum, 1.0)

    return c3_score, debug_weights
