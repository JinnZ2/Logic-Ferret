# sensor_suite/sensors/true_accountability_sensor.py

from typing import Tuple, Dict
import re

# Genuine accountability patterns
ACCOUNTABILITY_PATTERNS = [
    r"i was wrong about",
    r"i made a mistake",
    r"my error was",
    r"i take full responsibility",
    r"i should have",
    r"i failed to",
    r"this is on me",
    r"i own this failure",
]

# Giving credit to others
CREDIT_SHARING_PATTERNS = [
    r"the team deserves credit",
    r"thanks to my colleagues",
    r"my staff made this possible",
    r"others contributed",
    r"couldn't have done it without",
    r"team effort resulted",
    r"collaborative success",
]

# Intellectual humility
HUMILITY_PATTERNS = [
    r"i don't know",
    r"i'm not sure",
    r"i need to learn more",
    r"i was mistaken",
    r"let me find out",
    r"i'll get back to you",
    r"that's a good question",
    r"i hadn't considered that",
]

# Evidence of learning/adaptation
LEARNING_PATTERNS = [
    r"i've learned that",
    r"experience taught me",
    r"i now understand",
    r"this changed my view",
    r"i adapted by",
    r"feedback showed me",
    r"data indicated i was wrong",
]


def assess(text: str) -> Tuple[float, Dict[str, int]]:
    flags = {}
    lower_text = text.lower()

    accountability_hits = 0
    for pattern in ACCOUNTABILITY_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            accountability_hits += matches

    credit_sharing_hits = 0
    for pattern in CREDIT_SHARING_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            credit_sharing_hits += matches

    humility_hits = 0
    for pattern in HUMILITY_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            humility_hits += matches

    learning_hits = 0
    for pattern in LEARNING_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            learning_hits += matches

    total_accountability = accountability_hits + credit_sharing_hits + humility_hits + learning_hits

    # higher = more accountability detected (positive signal)
    score = min(total_accountability / 8.0, 1.0)

    flags["Takes Responsibility"] = accountability_hits
    flags["Shares Credit"] = credit_sharing_hits
    flags["Shows Humility"] = humility_hits
    flags["Demonstrates Learning"] = learning_hits
    flags["Total Accountability Score"] = f"{score:.2f}"

    return score, flags
