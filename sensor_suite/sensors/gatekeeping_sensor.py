# /sensors/gatekeeping_sensor.py

from typing import Tuple, Dict
import re

# Sample credentialist language
CREDENTIALISM_PHRASES = [
    "as an expert", "only qualified professionals", "not for beginners", 
    "must have a PhD", "you wouldn’t understand", "requires certification",
    "peer-reviewed only", "credentials required"
]

# Jargon patterns (these can be domain expanded)
TECH_JARGON = [
    "asymptotic", "orthogonal", "synergistic", "framework", "heuristic", 
    "ontology", "interoperability", "quantization", "elasticity", "scalability"
]

# Access restriction signals
ACCESS_CONTROL_PHRASES = [
    "members only", "behind paywall", "subscribe to access", "exclusive content", 
    "premium tier", "sign in to view", "confidential data", "nda required"
]

def assess(text: str) -> Tuple[float, Dict[str, str]]:
    flags = {}
    lower = text.lower()

    cred_hits = sum(1 for phrase in CREDENTIALISM_PHRASES if phrase in lower)
    jargon_hits = sum(1 for term in TECH_JARGON if re.search(rf"\b{term}\b", lower))
    access_hits = sum(1 for phrase in ACCESS_CONTROL_PHRASES if phrase in lower)

    # Score: weighted for presence and spread
    total_weight = (cred_hits * 1.3) + (jargon_hits * 1.5) + (access_hits * 1.4)
    total_possible = len(CREDENTIALISM_PHRASES) * 1.3 + len(TECH_JARGON) * 1.5 + len(ACCESS_CONTROL_PHRASES) * 1.4

    score = min(total_weight / total_possible, 1.0)

    flags["Credentialist Language"] = str(cred_hits)
    flags["Jargon Density"] = str(jargon_hits)
    flags["Access Restriction Phrases"] = str(access_hits)
    flags["Gatekeeping Index"] = f"{score:.2f}"

    return score, flags
