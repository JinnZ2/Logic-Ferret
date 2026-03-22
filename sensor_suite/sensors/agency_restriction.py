# /sensors/agency_detector.py

from typing import Tuple, Dict
import re

FALSE_CHOICE_PHRASES = [
    "you have no choice", "only one solution", "do this or fail", "you must choose", 
    "either you're with us", "we all have to do this"
]

COERCIVE_FRAMING = [
    "opt out disables service", "required to continue", "consent assumed", 
    "automatic enrollment", "you agree by using", "you can't say no"
]

REAL_AGENCY_CLUES = [
    "optional", "choose freely", "you can decline", "fully informed", 
    "open source", "non-binding", "no commitment required"
]

def assess(text: str) -> Tuple[float, Dict[str, str]]:
    lower = text.lower()

    false_choice = sum(1 for phrase in FALSE_CHOICE_PHRASES if phrase in lower)
    coercion = sum(1 for phrase in COERCIVE_FRAMING if phrase in lower)
    real_agency = sum(1 for phrase in REAL_AGENCY_CLUES if phrase in lower)

    total = false_choice + coercion + real_agency
    if total == 0:
        total = 1

    # Higher score = less agency
    agency_score = min((false_choice * 1.3 + coercion * 1.4) / total, 1.0)

    flags = {
        "False Choice Detected": str(false_choice),
        "Coercive Framing Instances": str(coercion),
        "Real Agency Indicators": str(real_agency),
        "Agency Restriction Score": f"{agency_score:.2f}"
    }

    return agency_score, flags

