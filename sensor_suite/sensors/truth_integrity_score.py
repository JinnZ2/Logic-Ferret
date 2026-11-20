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

# ------------------------------------------------------------
# WEIGHT_KEY (added 2026-11-20): one row per sensor name in
# run_full_sensor_scan.SENSORS -> the _WEIGHTS key it uses.
#
# Only pairs where the scan name and the _WEIGHTS key are the same
# string are mapped. A scan name with no _WEIGHTS key of the same
# name is VOID: no weight was ever written for it.
#
# Before this table, line 39 read `w = weights.get(name, 1.0)`, so
# the six VOID names (and any misspelt or new name) silently got 1.0.
# ------------------------------------------------------------
VOID = None

WEIGHT_KEY = {
    "Propaganda Tone":           "Propaganda Tone",
    "Reward Manipulation":       "Reward Manipulation",
    "False Urgency":             "False Urgency",
    "Gatekeeping":               "Gatekeeping",
    "Narrative Fragility":       "Narrative Fragility",
    "Agency Score":              "Agency Score",
    "Propaganda Bias":           "Propaganda Bias",
    "Logic Fallacy Ferret":      VOID,
    "Gaslight Frequency":        VOID,
    "Responsibility Deflection": VOID,
    "True Accountability":       VOID,
    "Meritocracy Detector":      VOID,
    "Conflict Diagnosis":        VOID,
}

# A VOID row has no weight in _WEIGHTS. Until a weight is decided,
# the value those six names received before (1.0, from the old
# default) is held here, by name, so the scan's C3 does not move in
# this change. This is the old behaviour written down, not a decision
# about what the weight should be.
VOID_HELD_WEIGHT = 1.0

# _WEIGHTS keys that no scan sensor maps to. "Discourse Collapse" is
# in schema_contract.SENSOR_REGISTRY but not in
# run_full_sensor_scan.SENSORS, so the scan never feeds it to C3.
ORPHAN_WEIGHT_KEYS = ("Discourse Collapse",)


class UnknownSensorName(KeyError):
    """A name passed to calculate_c3 is in neither WEIGHT_KEY nor _WEIGHTS."""


def resolve_weight(name: str) -> float:
    """Weight for one sensor name; raises on a name that is not listed.

    Order: a WEIGHT_KEY row (mapped key, or VOID -> VOID_HELD_WEIGHT),
    then a _WEIGHTS key used directly (how "Discourse Collapse" is
    reached). Anything else raises UnknownSensorName.
    """
    if name in WEIGHT_KEY:
        key = WEIGHT_KEY[name]
        if key is VOID:
            return VOID_HELD_WEIGHT
        return _WEIGHTS[key]
    if name in _WEIGHTS:
        return _WEIGHTS[name]
    raise UnknownSensorName(
        f"{name!r} has no row in WEIGHT_KEY and is not a _WEIGHTS key"
    )


def calculate_c3(sensor_scores: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    weighted_total = 0
    weight_sum = 0

    debug_weights = {}

    for name, score in sensor_scores.items():
        # was: w = weights.get(name, 1.0)   (unknown name -> 1.0)
        # 2026-11-20: an unknown name raises UnknownSensorName.
        w = resolve_weight(name)
        weighted_total += score * w
        weight_sum += w
        debug_weights[name] = round(score * w, 3)

    c3_score = min(weighted_total / weight_sum, 1.0)

    return c3_score, debug_weights
