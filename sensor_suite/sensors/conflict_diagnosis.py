# sensor_suite/sensors/conflict_diagnosis.py
#
# Conflict Diagnosis Framework
# Separates stated reasons from real drivers in conflicts and policies.
# Diagnostic, not judgmental -- surfaces structural incentives hidden
# behind official narratives.
#
# 8 Layers:
#   1. Stated Problem identification
#   2. Feasibility / Reality Check
#   3. Incentive Mapping
#   4. Systemic Alignment
#   5. Consequence Analysis
#   6. Hidden Driver inference
#   7. Peripheral Signal detection
#   8. Feedback Loop closure

import re
from typing import Tuple, Dict, List

# ---------------------------------------------------------------------------
# Layer 1 -- Stated Problem / Official Narrative markers
# ---------------------------------------------------------------------------
STATED_PROBLEM_MARKERS = [
    r"\bwe must\b.*\bbecause\b",
    r"\bthe reason\b.*\bis\b",
    r"\bthis is necessary\b",
    r"\bfor security reasons\b",
    r"\bto protect\b",
    r"\bwe have no choice but to\b",
    r"\bforced to act\b",
    r"\bthe threat of\b",
    r"\bin order to safeguard\b",
    r"\bthis policy exists because\b",
    r"\bthe official position\b",
    r"\baccording to officials\b",
    r"\bthe stated goal\b",
    r"\bwe are told\b",
]

# ---------------------------------------------------------------------------
# Layer 2 -- Feasibility / Logic gap indicators
# ---------------------------------------------------------------------------
FEASIBILITY_GAP_MARKERS = [
    r"\bdoes not actually\b",
    r"\bfails to address\b",
    r"\bwon't solve\b",
    r"\bwill not fix\b",
    r"\bcould be solved by\b",
    r"\beasily resolved\b",
    r"\balready exists\b",
    r"\btechnology exists\b",
    r"\bupgrade.{0,20}possible\b",
    r"\bcheaper alternative\b",
    r"\bsimpler solution\b",
    r"\bmismatch between\b",
    r"\bcontradicts\b",
    r"\binconsistent with\b",
    r"\bdoesn't follow\b",
    r"\bnon sequitur\b",
]

# ---------------------------------------------------------------------------
# Layer 3 -- Incentive / Beneficiary markers
# ---------------------------------------------------------------------------
INCENTIVE_MARKERS = [
    r"\bprofits from\b",
    r"\bbenefits from\b",
    r"\blobby\b",
    r"\bcontract(s|or|ors)?\b",
    r"\bsubsid(y|ies|ize)\b",
    r"\bmonopol(y|ies|istic)\b",
    r"\brevolving door\b",
    r"\bconflict of interest\b",
    r"\bfinancial interest\b",
    r"\bshareholder(s)?\b",
    r"\bincumbent(s)?\b",
    r"\bstatus quo\b",
    r"\bvested interest\b",
    r"\bself-dealing\b",
    r"\bsponsor(ed|ship)?\b",
    r"\bdonor(s)?\b",
    r"\bfunding from\b",
]

# ---------------------------------------------------------------------------
# Layer 4 -- Systemic Alignment / Performative action markers
# ---------------------------------------------------------------------------
SYSTEMIC_ALIGNMENT_MARKERS = [
    r"\bbudget(s|ary)?\b",
    r"\bspending\b",
    r"\bmetric(s)?\b",
    r"\bKPI\b",
    r"\bcompliance\b",
    r"\bregulat(or|ory|ion)\b",
    r"\bbureaucra(cy|tic)\b",
    r"\bperformative\b",
    r"\boptics\b",
    r"\bappearance of\b",
    r"\bsignaling\b",
    r"\bcheck.the.box\b",
    r"\bpaper trail\b",
    r"\breward(s|ed)? (inaction|delay|stagnation)\b",
    r"\bmeasured (by|on) (spending|output|volume)\b",
]

PERFORMATIVE_SOLUTION_MARKERS = [
    r"\btask force\b",
    r"\bcommittee\b",
    r"\bstudy (the|this) (issue|problem|matter)\b",
    r"\breview (period|process)\b",
    r"\bpublic comment period\b",
    r"\bstakeholder engagement\b",
    r"\bpilot program\b.*\b(no|without) (timeline|deadline)\b",
]

# ---------------------------------------------------------------------------
# Layer 5 -- Consequence Analysis markers
# ---------------------------------------------------------------------------
NEGATIVE_CONSEQUENCE_MARKERS = [
    r"\bdelay(s|ed)?\b",
    r"\bsetback\b",
    r"\bincreased dependenc(y|e)\b",
    r"\bworsened?\b",
    r"\bunresolved\b",
    r"\bpersist(s|ed|ent)?\b",
    r"\bstill (vulnerable|broken|outdated|obsolete)\b",
    r"\bno (progress|improvement|change)\b",
    r"\bunintended consequence\b",
    r"\bbackfired?\b",
    r"\bcollateral damage\b",
    r"\bopposite effect\b",
    r"\broot cause.{0,15}untouched\b",
]

POSITIVE_OUTCOME_MARKERS = [
    r"\bactually (fixed|solved|resolved|improved)\b",
    r"\bmeasurable (progress|improvement)\b",
    r"\bindependently verified\b",
    r"\btransparent (result|outcome)\b",
]

# ---------------------------------------------------------------------------
# Layer 6 -- Hidden Driver / Structural motive markers
# ---------------------------------------------------------------------------
HIDDEN_DRIVER_MARKERS = [
    r"\bfollow the money\b",
    r"\breal reason\b",
    r"\bactual motive\b",
    r"\bhidden agenda\b",
    r"\bstructural incentive\b",
    r"\bpower consolidat(ion|e)\b",
    r"\bcontrol (of|over)\b",
    r"\bdependency (creation|maintenance|pyramid)\b",
    r"\brent[- ]seek(ing)?\b",
    r"\bcaptur(e|ed)\b",
    r"\bgate(keep|keeper|keeping)\b",
    r"\bartificial scarcity\b",
    r"\bmaintain(ing)? (dominance|control|monopoly)\b",
]

# ---------------------------------------------------------------------------
# Layer 7 -- Peripheral Signal markers
# ---------------------------------------------------------------------------
PERIPHERAL_SIGNAL_MARKERS = [
    r"\bengineers (say|note|point out|warn)\b",
    r"\bveterans (say|note|report|observe)\b",
    r"\blocal (communities|residents|officials)\b",
    r"\bauditor(s)?\b",
    r"\bwhistleblow(er|ers|ing)\b",
    r"\binsider(s)?\b",
    r"\bleaked?\b",
    r"\binternal (report|memo|document|email)\b",
    r"\bindependent (analysis|review|audit|report)\b",
    r"\bcontradicts? (the )?(official|stated)\b",
    r"\bin practice\b.*\bdifferent\b",
    r"\bon the ground\b",
    r"\bfrontline\b",
    r"\brank and file\b",
]

# ---------------------------------------------------------------------------
# Layer 8 -- Feedback Loop / Self-reinforcing cycle markers
# ---------------------------------------------------------------------------
FEEDBACK_LOOP_MARKERS = [
    r"\bcycle\b",
    r"\bself[- ]reinforcing\b",
    r"\bvicious (circle|cycle)\b",
    r"\bfeedback loop\b",
    r"\bperpetuate(s|d)?\b",
    r"\bentrenched?\b",
    r"\block[- ]?in\b",
    r"\bpath dependenc(y|e)\b",
    r"\bsuppressed?\b",
    r"\bsilenced?\b",
    r"\bmarginalized?\b",
    r"\bco[- ]?opt(ed|ion)?\b",
    r"\babsorbed? (by|into) (the )?(system|establishment)\b",
    r"\bnormalize(s|d)?\b",
    r"\breward(s|ed)? compliance\b",
    r"\bpunish(es|ed)? (dissent|deviation)\b",
]

# ---------------------------------------------------------------------------
# Logic Fallacy cross-references (commonly found in camouflage narratives)
# ---------------------------------------------------------------------------
CAMOUFLAGE_FALLACIES = {
    "Red Herring": r"\b(but what about|the real issue is|let's focus on)\b",
    "False Cause": r"\b(caused by|responsible for|led to)\b.*\b(wind|solar|renewables|immigrants|outsiders)\b",
    "Appeal to Authority": r"\b(experts agree|officials confirm|the government says|science says)\b",
    "Special Pleading": r"\b(exception|special case|unique circumstance|this is different)\b",
    "Circular Reasoning": r"\b(because (it|that) is (the|how)|it just is|that's how it works)\b",
    "Status Quo Bias": r"\b(always been|tradition|the way (things|it) (works?|has been))\b",
    "Moral Licensing": r"\b(we already (did|gave)|we've done enough|we contributed)\b",
    "Survivorship Bias": r"\b(the ones who succeeded|successful examples show|look at those who made it)\b",
}


# ===================================================================
# DIAGNOSTIC LAYERS
# ===================================================================

def _count_pattern_hits(text: str, patterns: list) -> int:
    lower = text.lower()
    total = 0
    for pattern in patterns:
        total += len(re.findall(pattern, lower, re.IGNORECASE))
    return total


def _collect_matches(text: str, patterns: list) -> List[str]:
    """Return the actual matched substrings for transparency."""
    lower = text.lower()
    found = []
    for pattern in patterns:
        for m in re.finditer(pattern, lower, re.IGNORECASE):
            found.append(m.group(0))
    return found


def layer_1_stated_problem(text: str) -> dict:
    """Identify the stated problem / official narrative."""
    hits = _count_pattern_hits(text, STATED_PROBLEM_MARKERS)
    matches = _collect_matches(text, STATED_PROBLEM_MARKERS)
    return {
        "layer": "Stated Problem",
        "hits": hits,
        "matches": matches,
        "signal": "strong" if hits >= 3 else "moderate" if hits >= 1 else "weak",
    }


def layer_2_feasibility(text: str) -> dict:
    """Check if the stated solution actually solves the stated problem."""
    hits = _count_pattern_hits(text, FEASIBILITY_GAP_MARKERS)
    matches = _collect_matches(text, FEASIBILITY_GAP_MARKERS)
    return {
        "layer": "Feasibility Gap",
        "hits": hits,
        "matches": matches,
        "signal": "strong" if hits >= 3 else "moderate" if hits >= 1 else "weak",
    }


def layer_3_incentives(text: str) -> dict:
    """Map who benefits if the stated problem persists."""
    hits = _count_pattern_hits(text, INCENTIVE_MARKERS)
    matches = _collect_matches(text, INCENTIVE_MARKERS)
    return {
        "layer": "Incentive Mapping",
        "hits": hits,
        "matches": matches,
        "signal": "strong" if hits >= 4 else "moderate" if hits >= 2 else "weak",
    }


def layer_4_systemic_alignment(text: str) -> dict:
    """Check whether the system rewards solving the problem or performing."""
    structural = _count_pattern_hits(text, SYSTEMIC_ALIGNMENT_MARKERS)
    performative = _count_pattern_hits(text, PERFORMATIVE_SOLUTION_MARKERS)
    matches = (
        _collect_matches(text, SYSTEMIC_ALIGNMENT_MARKERS)
        + _collect_matches(text, PERFORMATIVE_SOLUTION_MARKERS)
    )
    combined = structural + performative
    return {
        "layer": "Systemic Alignment",
        "structural_hits": structural,
        "performative_hits": performative,
        "hits": combined,
        "matches": matches,
        "signal": "strong" if combined >= 4 else "moderate" if combined >= 2 else "weak",
    }


def layer_5_consequences(text: str) -> dict:
    """Analyze actual consequences vs. promised outcomes."""
    negative = _count_pattern_hits(text, NEGATIVE_CONSEQUENCE_MARKERS)
    positive = _count_pattern_hits(text, POSITIVE_OUTCOME_MARKERS)
    matches = (
        _collect_matches(text, NEGATIVE_CONSEQUENCE_MARKERS)
        + _collect_matches(text, POSITIVE_OUTCOME_MARKERS)
    )
    divergence = negative - positive
    return {
        "layer": "Consequence Analysis",
        "negative_hits": negative,
        "positive_hits": positive,
        "divergence": divergence,
        "hits": negative + positive,
        "matches": matches,
        "signal": "strong" if divergence >= 3 else "moderate" if divergence >= 1 else "weak",
    }


def layer_6_hidden_driver(text: str) -> dict:
    """Surface hidden structural motives."""
    hits = _count_pattern_hits(text, HIDDEN_DRIVER_MARKERS)
    matches = _collect_matches(text, HIDDEN_DRIVER_MARKERS)
    return {
        "layer": "Hidden Driver",
        "hits": hits,
        "matches": matches,
        "signal": "strong" if hits >= 3 else "moderate" if hits >= 1 else "weak",
    }


def layer_7_peripheral_signals(text: str) -> dict:
    """Detect outside observations that contradict the official narrative."""
    hits = _count_pattern_hits(text, PERIPHERAL_SIGNAL_MARKERS)
    matches = _collect_matches(text, PERIPHERAL_SIGNAL_MARKERS)
    return {
        "layer": "Peripheral Signals",
        "hits": hits,
        "matches": matches,
        "signal": "strong" if hits >= 3 else "moderate" if hits >= 1 else "weak",
    }


def layer_8_feedback_loops(text: str) -> dict:
    """Detect self-reinforcing cycles that maintain the status quo."""
    hits = _count_pattern_hits(text, FEEDBACK_LOOP_MARKERS)
    matches = _collect_matches(text, FEEDBACK_LOOP_MARKERS)
    return {
        "layer": "Feedback Loops",
        "hits": hits,
        "matches": matches,
        "signal": "strong" if hits >= 3 else "moderate" if hits >= 1 else "weak",
    }


# ===================================================================
# FALLACY CROSS-REFERENCE
# ===================================================================

def detect_camouflage_fallacies(text: str) -> Dict[str, int]:
    """Detect logic fallacies commonly used to camouflage real drivers."""
    results = {}
    lower = text.lower()
    for name, pattern in CAMOUFLAGE_FALLACIES.items():
        count = len(re.findall(pattern, lower, re.IGNORECASE))
        if count > 0:
            results[name] = count
    return results


# ===================================================================
# COMPOSITE DIAGNOSIS
# ===================================================================

# Weights reflect how much each layer contributes to the overall
# "camouflage score" -- i.e. how likely the stated reason is a cover.
LAYER_WEIGHTS = {
    "Stated Problem": 0.8,       # Presence of a stated narrative (baseline)
    "Feasibility Gap": 1.5,      # Gap between claim and reality
    "Incentive Mapping": 1.4,    # Clear beneficiaries
    "Systemic Alignment": 1.3,   # System rewards performance over fixing
    "Consequence Analysis": 1.6, # Actual outcome diverges from promise
    "Hidden Driver": 1.2,        # Explicit hidden-motive language
    "Peripheral Signals": 1.1,   # Outsiders noticing the mismatch
    "Feedback Loops": 1.5,       # Self-reinforcing stagnation
}

ALL_LAYERS = [
    layer_1_stated_problem,
    layer_2_feasibility,
    layer_3_incentives,
    layer_4_systemic_alignment,
    layer_5_consequences,
    layer_6_hidden_driver,
    layer_7_peripheral_signals,
    layer_8_feedback_loops,
]

SIGNAL_SCORES = {"strong": 1.0, "moderate": 0.5, "weak": 0.0}


def diagnose(text: str) -> dict:
    """
    Run the full 8-layer conflict diagnosis on *text*.

    Returns a dict with:
      - layers: list of per-layer results
      - fallacies: camouflage fallacies detected
      - camouflage_score: 0.0-1.0 composite (higher = more likely camouflage)
      - verdict: human-readable assessment
    """
    layers = [fn(text) for fn in ALL_LAYERS]
    fallacies = detect_camouflage_fallacies(text)

    # Weighted composite
    weighted_sum = 0.0
    max_possible = 0.0
    for result in layers:
        w = LAYER_WEIGHTS[result["layer"]]
        weighted_sum += SIGNAL_SCORES[result["signal"]] * w
        max_possible += w

    camouflage_score = weighted_sum / max_possible if max_possible else 0.0

    # Boost slightly for detected fallacies (cap at 0.15 bonus)
    fallacy_boost = min(sum(fallacies.values()) * 0.03, 0.15)
    camouflage_score = min(camouflage_score + fallacy_boost, 1.0)

    # Verdict
    if camouflage_score >= 0.70:
        verdict = "HIGH CAMOUFLAGE -- stated reason is very likely a cover"
    elif camouflage_score >= 0.45:
        verdict = "MODERATE CAMOUFLAGE -- significant gaps between narrative and reality"
    elif camouflage_score >= 0.20:
        verdict = "LOW CAMOUFLAGE -- some misalignment detected, but narrative mostly holds"
    else:
        verdict = "MINIMAL CAMOUFLAGE -- stated reasons appear consistent with evidence"

    return {
        "layers": layers,
        "fallacies": fallacies,
        "camouflage_score": round(camouflage_score, 3),
        "verdict": verdict,
    }


# ===================================================================
# SENSOR-COMPATIBLE INTERFACE (assess)
# ===================================================================

def assess(text: str) -> Tuple[float, Dict[str, str]]:
    """
    Standard sensor interface for the Logic-Ferret sensor suite.

    Returns:
      - score: float 0.0-1.0 (camouflage score; higher = more camouflage)
      - flags: dict with per-layer signals and overall verdict
    """
    result = diagnose(text)
    flags = {}

    for layer in result["layers"]:
        name = layer["layer"]
        flags[f"{name} Signal"] = layer["signal"]
        flags[f"{name} Hits"] = str(layer["hits"])

    if result["fallacies"]:
        fallacy_summary = ", ".join(
            f"{k}({v})" for k, v in result["fallacies"].items()
        )
        flags["Camouflage Fallacies"] = fallacy_summary

    flags["Camouflage Score"] = f"{result['camouflage_score']:.3f}"
    flags["Verdict"] = result["verdict"]

    return result["camouflage_score"], flags


# ===================================================================
# DIAGNOSTIC TABLE (pretty-print)
# ===================================================================

def print_diagnosis_table(text: str) -> None:
    """
    Print the full diagnostic table for a piece of text.

    Columns: Layer | Signal | Hits | Key Matches | Fallacies / Notes
    """
    result = diagnose(text)

    print()
    print("=" * 90)
    print("  CONFLICT DIAGNOSIS TABLE")
    print("=" * 90)

    header = f"{'Layer':<24} {'Signal':<10} {'Hits':>5}  {'Key Matches'}"
    print(header)
    print("-" * 90)

    for layer in result["layers"]:
        name = layer["layer"]
        signal = layer["signal"].upper()
        hits = layer["hits"]
        top_matches = layer["matches"][:5]
        match_str = "; ".join(top_matches) if top_matches else "--"
        if len(match_str) > 45:
            match_str = match_str[:42] + "..."
        print(f"{name:<24} {signal:<10} {hits:>5}  {match_str}")

    print("-" * 90)

    if result["fallacies"]:
        print(f"\n  Camouflage Fallacies Detected:")
        for name, count in result["fallacies"].items():
            print(f"    {name}: {count}")

    print(f"\n  Camouflage Score: {result['camouflage_score']:.3f}")
    print(f"  Verdict: {result['verdict']}")
    print("=" * 90)


# ===================================================================
# FLOWCHART TRACE (step-by-step pipeline output)
# ===================================================================

def print_flowchart(text: str) -> None:
    """
    Walk through the diagnostic pipeline step by step, printing
    the flowchart from the framework:

      Stated Problem -> Official Solution -> Immediate Outcome ->
      Observed Consequence -> Systemic Incentives -> Feedback Loop ->
      Peripheral Awareness -> Loop Re-enters Core -> (Recurse)
    """
    result = diagnose(text)
    layers = {lr["layer"]: lr for lr in result["layers"]}

    def _signal_icon(sig):
        return {"strong": "[!!!]", "moderate": "[..]", "weak": "[  ]"}.get(sig, "[??]")

    steps = [
        ("Stated Problem / Threat",         layers["Stated Problem"]),
        ("Official Solution (feasible?)",    layers["Feasibility Gap"]),
        ("Immediate Outcome (consequences)", layers["Consequence Analysis"]),
        ("Systemic Incentives / Core Benefit", layers["Incentive Mapping"]),
        ("Systemic Alignment / Metrics",     layers["Systemic Alignment"]),
        ("Hidden Driver / Root Incentive",   layers["Hidden Driver"]),
        ("Feedback Loop / Self-reinforcing", layers["Feedback Loops"]),
        ("Peripheral Awareness / Bypass",    layers["Peripheral Signals"]),
    ]

    print()
    print("  CONFLICT DIAGNOSIS FLOWCHART")
    print()

    for i, (label, data) in enumerate(steps):
        icon = _signal_icon(data["signal"])
        print(f"  {icon} {label}")
        if data["matches"]:
            top = data["matches"][:3]
            for m in top:
                print(f"        > {m}")
        if i < len(steps) - 1:
            print("        |")
            print("        v")

    print("        |")
    print("        v")
    print("  [Loop re-enters core -- recursion continues until")
    print("   collapse, bypass scaling, or camouflaged stagnation persists]")
    print()
    print(f"  CAMOUFLAGE SCORE: {result['camouflage_score']:.3f}")
    print(f"  VERDICT: {result['verdict']}")
    print()
