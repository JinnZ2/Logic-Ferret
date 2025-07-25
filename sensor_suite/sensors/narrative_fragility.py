# /sensors/narrative_fragility.py

from typing import Tuple, Dict
import re

LOGICAL_CONNECTORS = ["therefore", "thus", "because", "as a result", "proves that", "means that"]
WEAK_TRANSITIONS = ["some say", "it’s believed", "many agree", "people are saying", "obviously", "clearly"]
EVIDENCE_GAPS = ["no data", "unverified", "no evidence", "without proof", "allegedly"]
ABSURD_EXTRAPOLATIONS = ["so the world must", "this means everything changes", "proves all", "changes everything"]

def assess(text: str) -> Tuple[float, Dict[str, str]]:
    flags = {}
    lower = text.lower()

    weak_transitions = sum(1 for phrase in WEAK_TRANSITIONS if phrase in lower)
    missing_evidence = sum(1 for phrase in EVIDENCE_GAPS if phrase in lower)
    sketchy_logic = sum(1 for phrase in LOGICAL_CONNECTORS if re.search(rf"{phrase}\s+[a-z]", lower))
    wild_conclusions = sum(1 for phrase in ABSURD_EXTRAPOLATIONS if phrase in lower)

    total_weight = (weak_transitions * 1.3) + (missing_evidence * 1.5) + (sketchy_logic * 1.2) + (wild_conclusions * 1.6)
    total_possible = len(WEAK_TRANSITIONS) * 1.3 + len(EVIDENCE_GAPS) * 1.5 + len(LOGICAL_CONNECTORS) * 1.2 + len(ABSURD_EXTRAPOLATIONS) * 1.6

    score = min(total_weight / total_possible, 1.0)

    flags["Weak Transitions Detected"] = str(weak_transitions)
    flags["Evidence Gaps"] = str(missing_evidence)
    flags["Logical Stretch Points"] = str(sketchy_logic)
    flags["Overblown Conclusions"] = str(wild_conclusions)
    flags["Narrative Fragility Score"] = f"{score:.2f}"

    return score, flags
