# /sensors/reward_manipulation.py

from typing import Tuple, Dict
import re

# Triggers that indicate reward bait
FOMO_TRIGGERS = [
    "limited time", "last chance", "offer ends soon", "don't miss out", "only available today",
    "act now", "while supplies last", "exclusive access"
]

SOCIAL_PROOF_PHRASES = [
    "join 10,000 others", "everyone’s using", "most popular", "our top choice", "trending now"
]

EMOTIONAL BRIBES = [
    "you deserve", "you owe it to yourself", "real men/women", "true patriot", "prove you care"
]

INSTANT GRATIFICATION LANGUAGE = [
    "right now", "immediately", "fastest", "instant access", "get results today"
]

def assess(text: str) -> Tuple[float, Dict[str, str]]:
    flags = {}
    lower = text.lower()

    fomo_hits = sum(1 for phrase in FOMO_TRIGGERS if phrase in lower)
    social_hits = sum(1 for phrase in SOCIAL_PROOF_PHRASES if phrase in lower)
    bribe_hits = sum(1 for phrase in EMOTIONAL BRIBES if phrase in lower)
    gratification_hits = sum(1 for phrase in INSTANT GRATIFICATION LANGUAGE if phrase in lower)

    total_weight = (fomo_hits * 1.5) + (social_hits * 1.2) + (bribe_hits * 1.3) + (gratification_hits * 1.4)
    total_possible = len(FOMO_TRIGGERS) * 1.5 + len(SOCIAL_PROOF_PHRASES) * 1.2 + len(EMOTIONAL BRIBES) * 1.3 + len(INSTANT GRATIFICATION LANGUAGE) * 1.4

    score = min(total_weight / total_possible, 1.0)

    flags["FOMO Triggers"] = str(fomo_hits)
    flags["Social Pressure Hooks"] = str(social_hits)
    flags["Emotional Bribes"] = str(bribe_hits)
    flags["Instant Gratification Promises"] = str(gratification_hits)
    flags["Dopamine Lure Score"] = f"{score:.2f}"

    return score, flags
