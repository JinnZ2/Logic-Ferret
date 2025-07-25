# sensor_suite/sensors/fallacy_overlay.py

import re
from typing import Tuple, Dict

FALLACY_PATTERNS = {
    "Strawman": r"\b(so what you're saying is|let me get this straight)\b",
    "Ad Hominem": r"\b(you're just|you must be|only an idiot would)\b",
    "Slippery Slope": r"\b(if we allow this|what's next)\b",
    "Appeal to Emotion": r"\b(think of the children|how would you feel)\b",
    "False Dichotomy": r"\b(either.*or|you must choose)\b",
    "Circular Reasoning": r"\b(because I said so|it just is)\b",
    "Bandwagon": r"\b(everyone knows|obviously)\b",
}

def annotate_text(text: str) -> Tuple[str, Dict[str, int]]:
    counts = {}
    annotated = text

    for fallacy, pattern in FALLACY_PATTERNS.items():
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        counts[fallacy] = len(matches)

        # Basic annotation — wrap in markers
        for match in reversed(matches):  # reverse to not mess up positions
            start, end = match.span()
            tag = f"[{fallacy.upper()}]"
            annotated = annotated[:start] + tag + annotated[start:end] + tag + annotated[end:]

    return annotated, counts
