# sensor_suite/sensors/meritocracy_detector.py

from typing import Tuple, Dict
import re

# Actual competence indicators
COMPETENCE_PATTERNS = [
    r"here's the data",
    r"evidence shows",
    r"results indicate",
    r"testing revealed",
    r"measurements confirm",
    r"proven track record",
    r"demonstrable results",
    r"verifiable outcomes",
]

# Appeals to false authority instead of merit
FALSE_AUTHORITY_PATTERNS = [
    r"trust me, i'm an expert",
    r"because i said so",
    r"my credentials speak",
    r"i'm the authority",
    r"my position gives me",
    r"years of experience prove",
    r"my degree means",
    r"as someone with a title",
]

# Nepotism/favoritism indicators
FAVORITISM_PATTERNS = [
    r"old friend of mine",
    r"family connection",
    r"went to school together",
    r"longtime associate",
    r"personal relationship",
    r"inner circle",
    r"handpicked by me",
]

# Merit-based decision making
MERIT_PATTERNS = [
    r"best qualified candidate",
    r"highest performance",
    r"strongest results",
    r"most capable person",
    r"earned this position",
    r"proven ability",
    r"demonstrated competence",
    r"objective evaluation",
]


def assess(text: str) -> Tuple[float, Dict[str, int]]:
    flags = {}
    lower_text = text.lower()

    competence_hits = 0
    for pattern in COMPETENCE_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            competence_hits += matches

    merit_hits = 0
    for pattern in MERIT_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            merit_hits += matches

    false_authority_hits = 0
    for pattern in FALSE_AUTHORITY_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            false_authority_hits += matches

    favoritism_hits = 0
    for pattern in FAVORITISM_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            favoritism_hits += matches

    positive_signals = competence_hits + merit_hits
    negative_signals = false_authority_hits + favoritism_hits

    # higher positive, lower negative = better meritocracy
    raw_score = (positive_signals - negative_signals) / max(positive_signals + negative_signals, 1)
    score = max(0.0, min(raw_score, 1.0))

    flags["Competence Indicators"] = competence_hits
    flags["Merit-Based Language"] = merit_hits
    flags["False Authority Appeals"] = false_authority_hits
    flags["Favoritism Signals"] = favoritism_hits
    flags["Meritocracy Score"] = f"{score:.2f}"

    return score, flags
