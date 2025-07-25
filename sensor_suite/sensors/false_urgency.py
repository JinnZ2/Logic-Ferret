# /sensors/false_urgency.py

from typing import Tuple, Dict
import re

# Words that scream PANIC without explanation
HYPE_URGENCY = [
    "now", "immediately", "before it's too late", "today only", "act fast", 
    "won’t last", "right now", "time is running out", "before it's gone", 
    "urgent", "deadline", "vanishing", "limited time", "final call"
]

# Time-based pressure with no justification
FAKE_COUNTDOWN_PHRASES = [
    "ends in", "only [0-9]+ hours left", "offer expires", "sale ends soon",
    "last chance", "you have [0-9]+ minutes", "expiring soon"
]

# Overused catastrophic phrasing
CRISIS_WORDS = [
    "collapse", "emergency", "meltdown", "grid down", "total failure", "shutdown",
    "economic implosion", "end of freedom"
]

def assess(text: str) -> Tuple[float, Dict[str, str]]:
    flags = {}
    lower = text.lower()

    # Basic trigger scanning
    hype_hits = sum(1 for phrase in HYPE_URGENCY if phrase in lower)
    crisis_hits = sum(1 for word in CRISIS_WORDS if word in lower)
    countdown_hits = len(re.findall(r"(\d{1,2})\s?(minutes|hours|days)", lower)) + \
                     sum(1 for phrase in FAKE_COUNTDOWN_PHRASES if re.search(phrase, lower))

    total_weight = (hype_hits * 1.4) + (countdown_hits * 1.6) + (crisis_hits * 1.2)
    max_possible = len(HYPE_URGENCY) * 1.4 + len(FAKE_COUNTDOWN_PHRASES) * 1.6 + len(CRISIS_WORDS) * 1.2

    score = min(total_weight / max_possible, 1.0)

    flags["Hype Phrases"] = str(hype_hits)
    flags["Crisis Language"] = str(crisis_hits)
    flags["Time Constraint Triggers"] = str(countdown_hits)
    flags["Urgency Realness Score"] = f"{score:.2f}"

    return score, flags
