# sensor_suite/sensors/conflict_diagnosis.py
# ============================================================
# CONFLICT DIAGNOSIS FRAMEWORK
# "The problem is never what it claims to be."
# ============================================================
#
# WHY A FERRET?
#   A ferret is a physics exploit wrapped in fur.
#
#   - FLEXIBLE SPINE: 30 vertebrae, can bend nearly 180 degrees.
#     Squeezes through gaps that seem sealed shut -- like the gap
#     between a stated reason and the real one.
#
#   - TUNNELING: Evolved to hunt in burrows. It doesn't go around
#     the problem, it goes through it. Straight into the dark
#     where the thing is hiding.
#
#   - PERSISTENCE: Once locked on, a ferret doesn't quit. It will
#     follow a trail through twists, dead ends, and misdirection
#     until it reaches the source.
#
#   - STASHING: Ferrets hoard. They collect and cache objects in
#     hidden spots. This sensor collects receipts -- every matched
#     pattern is evidence stashed for the diagnostic table.
#
#   - WAR DANCE: The "weasel war dance" -- erratic, unpredictable
#     lateral movement. Approaches the problem from angles the
#     narrative didn't account for. Eight layers, eight angles.
#
#   - SCENT TRACKING: Ferrets locate prey by scent through walls
#     of dirt. This framework tracks incentive trails through walls
#     of institutional language.
#
#   - FERRETING OUT: The verb exists because the animal does.
#     "To ferret out" = to search tenaciously for something hidden.
#     That's the whole job.
#
# HOW IT WORKS:
#   Feed it text. Eight diagnostic layers flex through the
#   narrative like a ferret through a burrow. Each layer checks
#   for a different type of camouflage. The more layers light up,
#   the higher the Camouflage Score.
#
# LAYERS (pipeline order):
#   1. Stated Problem     -- what you're told to worry about
#   2. Feasibility Gap    -- does the "fix" actually fix anything?
#   3. Incentive Mapping  -- who gets paid if nothing changes?
#   4. Systemic Alignment -- does the system reward solving or stalling?
#   5. Consequence Check  -- what actually happened vs. what was promised
#   6. Hidden Driver      -- the real reason, under the hood
#   7. Peripheral Signals -- the people on the ground calling bullshit
#   8. Feedback Loops     -- the self-reinforcing cycle that keeps it stuck
#
# INTERFACE:
#   assess(text)              -> (score, flags)     # sensor suite compat
#   diagnose(text)            -> full structured dict
#   print_diagnosis_table()   -> formatted table
#   print_flowchart()         -> step-by-step pipeline trace

import re
from typing import Tuple, Dict, List


# ============================================================
# PATTERN REGISTRY
# ============================================================
# Each layer has a list of regex patterns grouped by semantic
# intent. Extend any list without guessing categories.
# ============================================================

# [LAYER 1] STATED PROBLEM
# The official story. The thing they want you focused on.
STATED_PROBLEM_MARKERS = [
    # justification framing
    r"\bwe must\b.*\bbecause\b",
    r"\bthe reason\b.*\bis\b",
    r"\bthis is necessary\b",
    r"\bthis policy exists because\b",
    # authority invocation
    r"\bfor security reasons\b",
    r"\bto protect\b",
    r"\bin order to safeguard\b",
    r"\baccording to officials\b",
    r"\bthe official position\b",
    # urgency / compulsion
    r"\bwe have no choice but to\b",
    r"\bforced to act\b",
    r"\bthe threat of\b",
    # narrative markers
    r"\bthe stated goal\b",
    r"\bwe are told\b",
]

# [LAYER 2] FEASIBILITY GAP
# The fix doesn't fix the stated problem. The ferret's spine
# bends through this gap -- if it fits, the gap is real.
FEASIBILITY_GAP_MARKERS = [
    # solution-problem mismatch
    r"\bdoes not actually\b",
    r"\bfails to address\b",
    r"\bwon't solve\b",
    r"\bwill not fix\b",
    r"\bdoesn't follow\b",
    r"\bnon sequitur\b",
    # cheaper / simpler path exists
    r"\bcould be solved by\b",
    r"\beasily resolved\b",
    r"\bcheaper alternative\b",
    r"\bsimpler solution\b",
    # the fix already exists (whoops)
    r"\balready exists\b",
    r"\btechnology exists\b",
    r"\bupgrade.{0,20}possible\b",
    # logical inconsistency
    r"\bmismatch between\b",
    r"\bcontradicts\b",
    r"\binconsistent with\b",
]

# [LAYER 3] INCENTIVE MAPPING
# Follow the scent trail. Who profits from the stated "solution"?
INCENTIVE_MARKERS = [
    # direct benefit
    r"\bprofits from\b",
    r"\bbenefits from\b",
    r"\bfinancial interest\b",
    r"\bvested interest\b",
    r"\bself-dealing\b",
    # institutional plumbing
    r"\blobby\b",
    r"\bcontract(s|or|ors)?\b",
    r"\bsubsid(y|ies|ize)\b",
    r"\brevolving door\b",
    r"\bconflict of interest\b",
    # market structure
    r"\bmonopol(y|ies|istic)\b",
    r"\bincumbent(s)?\b",
    r"\bstatus quo\b",
    # funding trails
    r"\bshareholder(s)?\b",
    r"\bsponsor(ed|ship)?\b",
    r"\bdonor(s)?\b",
    r"\bfunding from\b",
]

# [LAYER 4] SYSTEMIC ALIGNMENT
# Is the system measuring outcomes, or just measuring activity?
SYSTEMIC_ALIGNMENT_MARKERS = [
    # metrics & measurement theater
    r"\bbudget(s|ary)?\b",
    r"\bspending\b",
    r"\bmetric(s)?\b",
    r"\bKPI\b",
    r"\bmeasured (by|on) (spending|output|volume)\b",
    # bureaucratic machinery
    r"\bcompliance\b",
    r"\bregulat(or|ory|ion)\b",
    r"\bbureaucra(cy|tic)\b",
    r"\bpaper trail\b",
    # performance over substance
    r"\bperformative\b",
    r"\boptics\b",
    r"\bappearance of\b",
    r"\bsignaling\b",
    r"\bcheck.the.box\b",
    r"\breward(s|ed)? (inaction|delay|stagnation)\b",
]

# Subset: solutions designed to look busy without solving anything
PERFORMATIVE_SOLUTION_MARKERS = [
    r"\btask force\b",
    r"\bcommittee\b",
    r"\bstudy (the|this) (issue|problem|matter)\b",
    r"\breview (period|process)\b",
    r"\bpublic comment period\b",
    r"\bstakeholder engagement\b",
    r"\bpilot program\b.*\b(no|without) (timeline|deadline)\b",
]

# [LAYER 5] CONSEQUENCE ANALYSIS
# What actually happened? Usually the opposite of what was promised.
NEGATIVE_CONSEQUENCE_MARKERS = [
    # delays & stagnation
    r"\bdelay(s|ed)?\b",
    r"\bsetback\b",
    r"\bno (progress|improvement|change)\b",
    r"\bunresolved\b",
    r"\bpersist(s|ed|ent)?\b",
    # things got worse
    r"\bincreased dependenc(y|e)\b",
    r"\bworsened?\b",
    r"\bstill (vulnerable|broken|outdated|obsolete)\b",
    r"\bbackfired?\b",
    r"\bopposite effect\b",
    # root cause untouched (chef's kiss of performative action)
    r"\bunintended consequence\b",
    r"\bcollateral damage\b",
    r"\broot cause.{0,15}untouched\b",
]

POSITIVE_OUTCOME_MARKERS = [
    r"\bactually (fixed|solved|resolved|improved)\b",
    r"\bmeasurable (progress|improvement)\b",
    r"\bindependently verified\b",
    r"\btransparent (result|outcome)\b",
]

# [LAYER 6] HIDDEN DRIVER
# The real reason. The thing at the bottom of the burrow.
HIDDEN_DRIVER_MARKERS = [
    # explicit callouts
    r"\bfollow the money\b",
    r"\breal reason\b",
    r"\bactual motive\b",
    r"\bhidden agenda\b",
    r"\bstructural incentive\b",
    # power mechanics
    r"\bpower consolidat(ion|e)\b",
    r"\bcontrol (of|over)\b",
    r"\bmaintain(ing)? (dominance|control|monopoly)\b",
    # extraction patterns
    r"\bdependency (creation|maintenance|pyramid)\b",
    r"\brent[- ]seek(ing)?\b",
    r"\bcaptur(e|ed)\b",
    r"\bgate(keep|keeper|keeping)\b",
    r"\bartificial scarcity\b",
]

# [LAYER 7] PERIPHERAL SIGNALS
# The canaries. People outside the core who see the mismatch --
# engineers, veterans, auditors, locals. They notice the system
# *could* solve it but chooses not to.
PERIPHERAL_SIGNAL_MARKERS = [
    # domain experts speaking up
    r"\bengineers (say|note|point out|warn)\b",
    r"\bveterans (say|note|report|observe)\b",
    r"\bauditor(s)?\b",
    # community-level observation
    r"\blocal (communities|residents|officials)\b",
    r"\bon the ground\b",
    r"\bfrontline\b",
    r"\brank and file\b",
    # leak / insider contradiction
    r"\bwhistleblow(er|ers|ing)\b",
    r"\binsider(s)?\b",
    r"\bleaked?\b",
    r"\binternal (report|memo|document|email)\b",
    # independent verification
    r"\bindependent (analysis|review|audit|report)\b",
    r"\bcontradicts? (the )?(official|stated)\b",
    r"\bin practice\b.*\bdifferent\b",
]

# [LAYER 8] FEEDBACK LOOPS
# The burrow that digs itself deeper. Deviation is punished.
# The loop keeps running until collapse or external bypass.
FEEDBACK_LOOP_MARKERS = [
    # cycle language
    r"\bcycle\b",
    r"\bself[- ]reinforcing\b",
    r"\bvicious (circle|cycle)\b",
    r"\bfeedback loop\b",
    r"\bpath dependenc(y|e)\b",
    # entrenchment
    r"\bperpetuate(s|d)?\b",
    r"\bentrenched?\b",
    r"\block[- ]?in\b",
    r"\bnormalize(s|d)?\b",
    # suppression of alternatives
    r"\bsuppressed?\b",
    r"\bsilenced?\b",
    r"\bmarginalized?\b",
    r"\bco[- ]?opt(ed|ion)?\b",
    r"\babsorbed? (by|into) (the )?(system|establishment)\b",
    # reward/punish asymmetry
    r"\breward(s|ed)? compliance\b",
    r"\bpunish(es|ed)? (dissent|deviation)\b",
]


# ============================================================
# CAMOUFLAGE FALLACIES
# ============================================================
# Logic fallacies that show up when someone's dressing a bad
# reason in a nice suit. The ferret's war dance -- approach
# from angles the narrative didn't plan for.

CAMOUFLAGE_FALLACIES = {
    "Red Herring":       r"\b(but what about|the real issue is|let's focus on)\b",
    "False Cause":       r"\b(caused by|responsible for|led to)\b.*\b(wind|solar|renewables|immigrants|outsiders)\b",
    "Appeal to Authority": r"\b(experts agree|officials confirm|the government says|science says)\b",
    "Special Pleading":  r"\b(exception|special case|unique circumstance|this is different)\b",
    "Circular Reasoning": r"\b(because (it|that) is (the|how)|it just is|that's how it works)\b",
    "Status Quo Bias":   r"\b(always been|tradition|the way (things|it) (works?|has been))\b",
    "Moral Licensing":   r"\b(we already (did|gave)|we've done enough|we contributed)\b",
    "Survivorship Bias": r"\b(the ones who succeeded|successful examples show|look at those who made it)\b",
}


# ============================================================
# SCORING CONFIG
# ============================================================
# Weights: how much each layer contributes to the camouflage
# score. Higher weight = stronger signal that something stinks.

LAYER_WEIGHTS = {
    "Stated Problem":      0.8,  # baseline -- you need a story to hide behind
    "Feasibility Gap":     1.5,  # the fix doesn't fix? the ferret fits through
    "Incentive Mapping":   1.4,  # scent trail leads to someone's wallet
    "Systemic Alignment":  1.3,  # the system rewards theater, not results
    "Consequence Analysis": 1.6, # promised X, delivered the opposite of X
    "Hidden Driver":       1.2,  # what's at the bottom of the burrow
    "Peripheral Signals":  1.1,  # the canaries in the coal mine
    "Feedback Loops":      1.5,  # the burrow that digs itself deeper
}

# Signal thresholds -> numeric score
SIGNAL_SCORES = {"strong": 1.0, "moderate": 0.5, "weak": 0.0}

# Per-layer hit thresholds: (strong, moderate)
LAYER_THRESHOLDS = {
    "Stated Problem":       (3, 1),
    "Feasibility Gap":      (3, 1),
    "Incentive Mapping":    (4, 2),
    "Systemic Alignment":   (4, 2),
    "Consequence Analysis": (3, 1),  # uses divergence, not raw hits
    "Hidden Driver":        (3, 1),
    "Peripheral Signals":   (3, 1),
    "Feedback Loops":       (3, 1),
}


# ============================================================
# INTERNALS
# ============================================================

def _count_hits(text: str, patterns: list) -> int:
    """Count total regex matches across all patterns."""
    total = 0
    for p in patterns:
        total += len(re.findall(p, text, re.IGNORECASE))
    return total


def _collect_matches(text: str, patterns: list) -> List[str]:
    """Return matched substrings. Receipts, not claims."""
    found = []
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            found.append(m.group(0))
    return found


def _classify(value: int, layer_name: str) -> str:
    """Classify a hit count into strong / moderate / weak."""
    strong, moderate = LAYER_THRESHOLDS[layer_name]
    if value >= strong:
        return "strong"
    if value >= moderate:
        return "moderate"
    return "weak"


# ============================================================
# LAYER FUNCTIONS
# ============================================================
# Each returns: {layer, hits, matches, signal, ...extras}
# The ferret tunnels through each one in sequence.

def layer_1_stated_problem(text: str) -> dict:
    """What's the official story?"""
    hits = _count_hits(text, STATED_PROBLEM_MARKERS)
    return {
        "layer": "Stated Problem",
        "hits": hits,
        "matches": _collect_matches(text, STATED_PROBLEM_MARKERS),
        "signal": _classify(hits, "Stated Problem"),
    }


def layer_2_feasibility(text: str) -> dict:
    """Does the fix actually fix? The ferret's spine test -- if it bends through, the gap is real."""
    hits = _count_hits(text, FEASIBILITY_GAP_MARKERS)
    return {
        "layer": "Feasibility Gap",
        "hits": hits,
        "matches": _collect_matches(text, FEASIBILITY_GAP_MARKERS),
        "signal": _classify(hits, "Feasibility Gap"),
    }


def layer_3_incentives(text: str) -> dict:
    """Follow the scent. Who gets paid when nothing changes?"""
    hits = _count_hits(text, INCENTIVE_MARKERS)
    return {
        "layer": "Incentive Mapping",
        "hits": hits,
        "matches": _collect_matches(text, INCENTIVE_MARKERS),
        "signal": _classify(hits, "Incentive Mapping"),
    }


def layer_4_systemic_alignment(text: str) -> dict:
    """Is the system rewarding solutions or rewarding stalling?"""
    structural = _count_hits(text, SYSTEMIC_ALIGNMENT_MARKERS)
    performative = _count_hits(text, PERFORMATIVE_SOLUTION_MARKERS)
    combined = structural + performative
    return {
        "layer": "Systemic Alignment",
        "hits": combined,
        "structural_hits": structural,
        "performative_hits": performative,
        "matches": (
            _collect_matches(text, SYSTEMIC_ALIGNMENT_MARKERS)
            + _collect_matches(text, PERFORMATIVE_SOLUTION_MARKERS)
        ),
        "signal": _classify(combined, "Systemic Alignment"),
    }


def layer_5_consequences(text: str) -> dict:
    """What actually happened vs. what was promised?"""
    negative = _count_hits(text, NEGATIVE_CONSEQUENCE_MARKERS)
    positive = _count_hits(text, POSITIVE_OUTCOME_MARKERS)
    divergence = negative - positive
    return {
        "layer": "Consequence Analysis",
        "hits": negative + positive,
        "negative_hits": negative,
        "positive_hits": positive,
        "divergence": divergence,
        "matches": (
            _collect_matches(text, NEGATIVE_CONSEQUENCE_MARKERS)
            + _collect_matches(text, POSITIVE_OUTCOME_MARKERS)
        ),
        "signal": _classify(divergence, "Consequence Analysis"),
    }


def layer_6_hidden_driver(text: str) -> dict:
    """What's at the bottom of the burrow?"""
    hits = _count_hits(text, HIDDEN_DRIVER_MARKERS)
    return {
        "layer": "Hidden Driver",
        "hits": hits,
        "matches": _collect_matches(text, HIDDEN_DRIVER_MARKERS),
        "signal": _classify(hits, "Hidden Driver"),
    }


def layer_7_peripheral_signals(text: str) -> dict:
    """The canaries. People outside the bubble who see the mismatch."""
    hits = _count_hits(text, PERIPHERAL_SIGNAL_MARKERS)
    return {
        "layer": "Peripheral Signals",
        "hits": hits,
        "matches": _collect_matches(text, PERIPHERAL_SIGNAL_MARKERS),
        "signal": _classify(hits, "Peripheral Signals"),
    }


def layer_8_feedback_loops(text: str) -> dict:
    """The burrow that digs itself deeper."""
    hits = _count_hits(text, FEEDBACK_LOOP_MARKERS)
    return {
        "layer": "Feedback Loops",
        "hits": hits,
        "matches": _collect_matches(text, FEEDBACK_LOOP_MARKERS),
        "signal": _classify(hits, "Feedback Loops"),
    }


# Pipeline order -- the ferret's path through the burrow
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


# ============================================================
# FALLACY CROSS-REFERENCE
# ============================================================

def detect_camouflage_fallacies(text: str) -> Dict[str, int]:
    """War dance: hit the narrative from angles it didn't plan for."""
    hits = {}
    for name, pattern in CAMOUFLAGE_FALLACIES.items():
        count = len(re.findall(pattern, text, re.IGNORECASE))
        if count:
            hits[name] = count
    return hits


# ============================================================
# COMPOSITE DIAGNOSIS
# ============================================================

# Verdicts -- what the ferret found
VERDICTS = [
    (0.70, "HIGH CAMOUFLAGE -- the stated reason is wearing a fake mustache. The ferret is not fooled."),
    (0.45, "MODERATE CAMOUFLAGE -- narrative and reality aren't on speaking terms. Something's in the burrow."),
    (0.20, "LOW CAMOUFLAGE -- a few cracks in the story. The ferret sniffed but didn't dig deep."),
    (0.00, "MINIMAL CAMOUFLAGE -- stated reasons check out. The ferret yawned and moved on."),
]


def diagnose(text: str) -> dict:
    """
    Full 8-layer conflict diagnosis.

    The ferret enters the burrow at Layer 1 and tunnels through
    all 8 layers, collecting evidence (matches) and classifying
    signal strength at each stage.

    Returns:
        layers:           list of per-layer result dicts
        fallacies:        {fallacy_name: count}
        camouflage_score: float 0.0-1.0 (higher = more camouflage)
        verdict:          human-readable assessment
    """
    layers = [fn(text) for fn in ALL_LAYERS]
    fallacies = detect_camouflage_fallacies(text)

    # weighted composite from layer signals
    weighted_sum = sum(
        SIGNAL_SCORES[lr["signal"]] * LAYER_WEIGHTS[lr["layer"]]
        for lr in layers
    )
    max_possible = sum(LAYER_WEIGHTS.values())
    score = weighted_sum / max_possible if max_possible else 0.0

    # fallacy bonus (capped at +0.15) -- war dance findings
    score = min(score + min(sum(fallacies.values()) * 0.03, 0.15), 1.0)

    verdict = next(v for threshold, v in VERDICTS if score >= threshold)

    return {
        "layers": layers,
        "fallacies": fallacies,
        "camouflage_score": round(score, 3),
        "verdict": verdict,
    }


# ============================================================
# SENSOR SUITE INTERFACE
# ============================================================
# Drop-in with every other Logic-Ferret sensor.
# assess(text) -> (score, flags)

def assess(text: str) -> Tuple[float, Dict[str, str]]:
    """
    Sensor-suite-compatible interface.

    Returns:
        score: float 0.0-1.0 (higher = more camouflage detected)
        flags: per-layer signals, fallacy summary, verdict
    """
    result = diagnose(text)
    flags = {}

    for lr in result["layers"]:
        name = lr["layer"]
        flags[f"{name} Signal"] = lr["signal"]
        flags[f"{name} Hits"] = str(lr["hits"])

    if result["fallacies"]:
        flags["Camouflage Fallacies"] = ", ".join(
            f"{k}({v})" for k, v in result["fallacies"].items()
        )

    flags["Camouflage Score"] = f"{result['camouflage_score']:.3f}"
    flags["Verdict"] = result["verdict"]

    return result["camouflage_score"], flags


# ============================================================
# OUTPUT: DIAGNOSTIC TABLE
# ============================================================

def _signal_icon(sig: str) -> str:
    """Ferret behavior state for each signal level."""
    return {
        "strong": "DIG",   # ferret is digging -- found something
        "moderate": "snf",  # sniffing -- something's there
        "weak": "zzz",     # napping -- nothing interesting
    }.get(sig, " ? ")


def print_diagnosis_table(text: str) -> None:
    """
    Formatted diagnostic table.
    Columns: Layer | Ferret | Hits | Evidence
    """
    result = diagnose(text)

    print()
    print("=" * 88)
    print("   CONFLICT DIAGNOSIS TABLE")
    print("   \"The problem is never what it claims to be.\"")
    print("=" * 88)
    print(f" {'Layer':<24}{'Ferret':<8}{'Hits':>5}   {'Evidence (stashed receipts)'}")
    print("-" * 88)

    for lr in result["layers"]:
        icon = _signal_icon(lr["signal"])
        top = lr["matches"][:4]
        evidence = "; ".join(top) if top else "-- (nothing to stash)"
        if len(evidence) > 42:
            evidence = evidence[:39] + "..."
        print(f" {lr['layer']:<24}[{icon}] {lr['hits']:>5}   {evidence}")

    print("-" * 88)

    if result["fallacies"]:
        print()
        print("   War Dance Findings (narrative fallacies):")
        for name, count in result["fallacies"].items():
            print(f"     {name}: {count}")

    print()
    print(f"   Camouflage Score: {result['camouflage_score']:.3f}")
    print(f"   {result['verdict']}")
    print("=" * 88)
    print()


# ============================================================
# OUTPUT: FLOWCHART TRACE
# ============================================================
# The ferret's path through the burrow, layer by layer.
# Stated problem -> does the fix work? -> who benefits?
# -> system alignment -> actual consequences -> hidden driver
# -> feedback loops -> peripheral signals -> (recurse)

FLOWCHART_STEPS = [
    ("Stated Problem / Threat",           "Stated Problem"),
    ("Official Solution -- does it fix?",  "Feasibility Gap"),
    ("Actual Consequences",                "Consequence Analysis"),
    ("Who Benefits? (scent trail)",        "Incentive Mapping"),
    ("System Rewards What?",               "Systemic Alignment"),
    ("Hidden Driver (bottom of burrow)",   "Hidden Driver"),
    ("Feedback Loop (self-digging)",       "Feedback Loops"),
    ("Peripheral Signals (canaries)",      "Peripheral Signals"),
]


def print_flowchart(text: str) -> None:
    """The ferret's tunnel path, step by step."""
    result = diagnose(text)
    by_name = {lr["layer"]: lr for lr in result["layers"]}

    print()
    print("   CONFLICT DIAGNOSIS FLOWCHART")
    print("   (the ferret enters the burrow)")
    print()

    for i, (label, layer_key) in enumerate(FLOWCHART_STEPS):
        data = by_name[layer_key]
        icon = _signal_icon(data["signal"])
        print(f"  [{icon}] {label}")
        for m in data["matches"][:3]:
            print(f"          > {m}")
        if i < len(FLOWCHART_STEPS) - 1:
            print("          |")
            print("          v")

    print("          |")
    print("          v")
    print("   [Loop re-enters core]")
    print("   The burrow circles back. Recursion continues until")
    print("   collapse, bypass, or camouflaged stagnation becomes normal.")
    print()
    print(f"   CAMOUFLAGE SCORE: {result['camouflage_score']:.3f}")
    print(f"   {result['verdict']}")
    print()
