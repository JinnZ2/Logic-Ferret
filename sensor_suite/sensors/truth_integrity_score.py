# /sensors/truth_integrity_score.py

from typing import Dict, Tuple

def calculate_c3(sensor_scores: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    weights = {
        "Propaganda Tone": 1.2,
        "Reward Manipulation": 1.0,
        "False Urgency": 1.1,
        "Gatekeeping": 1.3,
        "Narrative Fragility": 1.4,
        "Propaganda Bias": 1.5,
        "Agency Score": 1.6
    }

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
