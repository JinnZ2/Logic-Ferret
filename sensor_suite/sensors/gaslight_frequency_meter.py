# sensor_suite/sensors/gaslight_frequency_meter.py

from typing import Tuple, Dict
import re

GASLIGHT_PATTERNS = [
    r"\byou're imagining things\b",
    r"\bthat never happened\b",
    r"\byou're too sensitive\b",
    r"\byou always\b",
    r"\byou never\b",
    r"\bit's all in your head\b",
    r"\bno one else thinks that\b",
]

def assess(text: str) -> Tuple[float, Dict[str, int]]:
    flags = {}
    total_hits = 0

    for pattern in GASLIGHT_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        count = len(matches)
        if count:
            label = pattern.strip(r"\b").replace("\\", "")
            flags[label] = count
            total_hits += count

    score = max(0.0, 1.0 - min(total_hits / 5.0, 1.0))  # 1.0 = low gaslight, 0.0 = high

    return score, flags
