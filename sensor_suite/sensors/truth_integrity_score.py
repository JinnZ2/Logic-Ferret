# sensor_suite/sensors/truth_integrity_score.py
#
# Computes the C3 (Composite Truth Integrity) score using weighted averaging.
# Weight rationale: tactics that remove autonomy or distort reality score higher.
# See sensor_suite/weights.txt for detailed justification.

from typing import Dict, Tuple

# Canonical weight definitions for all sensors.
# Higher weight = greater impact on the composite score.
WEIGHTS = {
    "Propaganda Tone": 1.2,
    "Reward Manipulation": 1.0,
    "False Urgency": 1.1,
    "Gatekeeping": 1.3,
    "Narrative Fragility": 1.4,
    "Propaganda Bias": 1.5,
    "Agency Restriction": 1.6,
    "Fallacy Overlay": 1.3,
    "Gaslight Frequency": 1.5,
    "Responsibility Deflection": 1.2,
    "True Accountability": 1.0,
    "Meritocracy": 1.1,
}

# Sensors where higher score = positive signal (inverted for composite)
POSITIVE_SENSORS = {"True Accountability", "Meritocracy"}


def calculate_c3(sensor_scores: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    """
    Calculate the C3 composite truth integrity score.

    For most sensors, higher score = more problematic (adds to distortion).
    For positive sensors (accountability, meritocracy), the score is inverted
    so that high accountability *reduces* the composite distortion score.

    Returns:
        c3_score: float 0.0-1.0 (higher = more distortion detected)
        debug_weights: per-sensor weighted contribution breakdown
    """
    weighted_total = 0.0
    weight_sum = 0.0
    debug_weights = {}

    for name, score in sensor_scores.items():
        w = WEIGHTS.get(name, 1.0)

        # Invert positive sensors so high accountability lowers the composite
        effective_score = (1.0 - score) if name in POSITIVE_SENSORS else score

        weighted_total += effective_score * w
        weight_sum += w
        debug_weights[name] = round(effective_score * w, 3)

    c3_score = min(weighted_total / weight_sum, 1.0) if weight_sum else 0.0

    return c3_score, debug_weights
