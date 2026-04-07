# sensor_suite/sensors/responsibility_deflection_sensor.py

from typing import Tuple, Dict
import re

# Classic deflection phrases
DEFLECTION_PATTERNS = [
    r"due to external factors",
    r"market conditions forced",
    r"we inherited this situation",
    r"nobody could have predicted",
    r"unprecedented challenges",
    r"mistakes were made",
    r"errors occurred",
    r"the situation developed",
    r"circumstances beyond our control",
    r"global headwinds",
    r"temporary flux",
    r"challenging environment",
    r"perfect storm",
    r"black swan event",
]

# Credit-stealing patterns
CREDIT_GRAB_PATTERNS = [
    r"under my leadership",
    r"i delivered",
    r"my vision resulted",
    r"i orchestrated",
    r"thanks to my",
    r"my strategy led to",
]

# Passive voice responsibility dodging
PASSIVE_DODGE_PATTERNS = [
    r"mistakes were made",
    r"decisions were taken",
    r"problems were encountered",
    r"issues arose",
    r"challenges emerged",
    r"difficulties developed",
]


def assess(text: str) -> Tuple[float, Dict[str, int]]:
    flags = {}
    lower_text = text.lower()

    deflection_hits = 0
    for pattern in DEFLECTION_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            deflection_hits += matches

    credit_hits = 0
    for pattern in CREDIT_GRAB_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            credit_hits += matches

    passive_hits = 0
    for pattern in PASSIVE_DODGE_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            passive_hits += matches

    total_deflection = deflection_hits + credit_hits + passive_hits

    # higher = more deflection detected
    score = min(total_deflection / 10.0, 1.0)

    flags["Responsibility Deflection"] = deflection_hits
    flags["Credit Stealing"] = credit_hits
    flags["Passive Voice Dodging"] = passive_hits
    flags["Total Deflection Score"] = f"{score:.2f}"

    return score, flags
