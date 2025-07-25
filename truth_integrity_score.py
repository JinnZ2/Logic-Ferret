# sensor_suite/sensors/truth_integrity_score.py

from typing import Dict, Tuple

def calculate_c3(sensor_scores: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    weights = {
        k: 1.0 for k in sensor_scores  # simple equal-weighting
    }
    total_weight = sum(weights.values())

    weighted_scores = {
        k: sensor_scores[k] * weights[k]
        for k in sensor_scores
    }

    composite = sum(weighted_scores.values()) / total_weight if total_weight else 0.0
    normalized = {
        k: weights[k] / total_weight for k in sensor_scores
    }

    return composite, normalized
