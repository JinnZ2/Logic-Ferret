# sensor_suite/sensors/logic_fallacy_ferret.py

from .fallacy_overlay import annotate_text

def assess(text: str):
    annotated, counts = annotate_text(text)
    total = sum(counts.values())
    score = 1.0 - min(total / 10, 1.0)  # crude inverse score
    return score, counts
