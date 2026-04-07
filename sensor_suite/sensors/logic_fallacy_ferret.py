# sensor_suite/sensors/logic_fallacy_ferret.py

from .fallacy_overlay import annotate_text


def assess(text: str):
    annotated, counts = annotate_text(text)
    total = sum(counts.values())
    score = min(total / 10, 1.0)  # higher = more fallacies detected
    return score, counts
