# /sensors/propaganda_bias.py

from typing import Tuple, Dict
import re

INFORMATIVE_CLUES = [
    "according to", "data shows", "studies suggest", "research indicates", 
    "historical record", "peer-reviewed", "source: "
]

PERSUASIVE_TRIGGERS = [
    "you need to", "must act", "wake up", "join us", "take control", 
    "before it’s too late", "protect yourself", "defend your family"
]

MANIPULATIVE_CUES = [
    "everyone is against you", "you’re being lied to", "this is the only way", 
    "you’ve been tricked", "they control everything", "you can’t trust anyone"
]

def assess(text: str) -> Tuple[float, Dict[str, str]]:
    lower = text.lower()

    info_hits = sum(1 for phrase in INFORMATIVE_CLUES if phrase in lower)
    persuade_hits = sum(1 for phrase in PERSUASIVE_TRIGGERS if phrase in lower)
    manip_hits = sum(1 for phrase in MANIPULATIVE_CUES if phrase in lower)

    total = info_hits + persuade_hits + manip_hits
    if total == 0:
        total = 1  # prevent div by zero

    # Calculate bias weight: informative reduces bias, manipulative increases it
    bias_score = min((persuade_hits * 1.2 + manip_hits * 1.5) / total, 1.0)

    flags = {
        "Informative Language Hits": str(info_hits),
        "Persuasive Language Hits": str(persuade_hits),
        "Manipulation Cues": str(manip_hits),
        "Propaganda Bias Score": f"{bias_score:.2f}"
    }

    return bias_score, flags
