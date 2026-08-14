# /sensors/propaganda_tone.py

from typing import Tuple, Dict
import re

# Sample propaganda triggers (expandable)
FRAMING_PHRASES = [
    "they don't want you to know", "wake up", "the truth is", "everything you know is a lie",
    "mainstream media", "puppet masters", "red pill", "patriots", "elite agenda"
]

BINARY_OPPOSITIONS = ["us vs them", "good vs evil", "freedom vs control", "truth vs lies"]

EMOTIONAL_WORDS = [
    "betrayal", "corrupt", "hero", "evil", "savior", "tyranny", "liberty", "war", "rigged"
]

REPETITION_WARNINGS = ["wake up", "fight back", "the truth", "exposed", "the real story"]

def assess(text: str) -> Tuple[float, Dict[str, str]]:
    flags = {}
    lower_text = text.lower()

    # Count propaganda phrase hits
    framing_hits = sum(1 for phrase in FRAMING_PHRASES if phrase in lower_text)
    binary_hits = sum(1 for binary in BINARY_OPPOSITIONS if binary in lower_text)
    emotional_hits = sum(1 for word in EMOTIONAL_WORDS if re.search(rf"\b{word}\b", lower_text))
    repetition_hits = sum(lower_text.count(phrase) for phrase in REPETITION_WARNINGS if lower_text.count(phrase) > 1)

    total_weight = (framing_hits * 1.5) + (binary_hits * 1.2) + emotional_hits + (repetition_hits * 1.3)
    total_possible = len(FRAMING_PHRASES) * 1.5 + len(BINARY_OPPOSITIONS) * 1.2 + len(EMOTIONAL_WORDS) + len(REPETITION_WARNINGS) * 1.3

    score = min(total_weight / total_possible, 1.0)

    flags["Framing Phrases Detected"] = str(framing_hits)
    flags["Binary Logic Framing"] = str(binary_hits)
    flags["Emotional Language Hits"] = str(emotional_hits)
    flags["Repetitive Phrase Alerts"] = str(repetition_hits)
    flags["Framing Index"] = f"{score:.2f}"

    return score, flags
