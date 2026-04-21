# sensor_suite/sensors/discourse_collapse.py
# ============================================================
# LAYER 9 -- DISCOURSE COLLAPSE
# "The burrow has caved in. There's no real reason hiding
# behind the stated one because the machinery for distinguishing
# reasons has been destroyed."
# ============================================================
#
# Pipeline position: runs AFTER the 8 camouflage layers in
# conflict_diagnosis. Layers 1-8 measure "stated vs. real reason"
# mismatch (camouflage). Layer 9 measures whether that distinction
# is still operational at all.
#
# First-principles purpose of rhetoric: substituting discourse
# for force as a coordination mechanism -- transmitting claims
# across minds in a form the receiver can evaluate, accept,
# reject, or revise. Discourse collapse is when that apparatus
# is no longer reachable from within the system.
#
# BLACK TIER: Logic-Ferret emits BLACK only from this module.
# The other 8 camouflage layers cap at RED. BLACK is reserved
# for state where the rhetoric's own mechanism (argument, evidence,
# revision) cannot restore it -- analogous to metabolic-accounting
# past-cliff basins and TAF thermodynamic irreversibility.
#
# SUB-DETECTORS (four, not three -- 9d added from design review):
#   9a  Semantic Inversion         -- words severed from referents
#   9b  Self-Sealing Absorption    -- counter-evidence absorbed as proof
#   9c  Action Licensing           -- rhetoric -> precursor of force
#   9d  Critical-Thinking Suppression -- attack on reasoning itself
#
# EFFECT GRADIENT (why weighting matters more than marker count):
#   The harm function isn't "did this text pass a threshold?" --
#   it's "does this rhetoric, once ingested by an AI system or a
#   susceptible human, damage the cognitive substrate that makes
#   critical thinking possible?"
#
#   9b (self-sealing) has the highest slope: every instance trains
#   an absorption rule (doubt -> proves the conspiracy). Models
#   pattern-completing on it learn to treat disagreement as
#   confirming signal. Humans marinating in it lose revision.
#
#   9d (critical-thinking suppression) is the direct attack: it
#   names and dismisses the cognitive operations by name.
#   9b + 9d together is the cognition-attack profile.
#
#   9a (semantic inversion) poisons encoding -- inverted keys
#   corrupt embeddings and corrupt the reader's ability to name
#   what they're seeing.
#
#   9c (action licensing) is a different harm class: violence
#   coordination, not cognition erosion. Own threshold.
#
# REPORTAGE GUARDRAIL: a parallel detector for quote markers and
# analytic framing. If strong, de-escalates tier by one step
# (BLACK -> RED). Protects news reports, scholarly analysis,
# and satire quoting the very patterns this layer detects.
#
# FRACTAL OBLIGATION: Ferret's output is itself consumed by AI
# systems that may relay it to susceptible humans. Every BLACK
# elevation exposes which sub-detectors fired, which specific
# markers matched, and which elevation clause triggered. No
# opaque verdict. The output shape IS part of the anti-erosion
# function.
# ============================================================

import re
from typing import Dict, List, Tuple


# ============================================================
# 9a. SEMANTIC INVERSION
# ============================================================
# Regex can only catch flagrant lexical cases. Most semantic
# inversion needs corpus-level drift analysis; this is v1 only.
# ============================================================

# Adjacency patterns: word X within ~80 chars of its antonym.
# Single-regex proximity via .{0,80}.
SEMANTIC_INVERSION_MARKERS = [
    r"\bpeaceful\b.{0,80}\b(violence|killing|force|crush|destroy)\b",
    r"\b(violence|killing|force|crush|destroy)\b.{0,80}\bpeaceful\b",
    r"\bfreedom\b.{0,80}\b(surveillance|monitor(ing)?|track(ing)?|register(ed|ing)?)\b",
    r"\bprotect(ion)?\b.{0,80}\b(harm|eliminate|destroy|remove|purge)\b",
    r"\bdemocra(cy|tic)\b.{0,80}\b(suppress|silence|eliminate)\b.{0,40}\b(opposition|dissent)\b",
    # documented historical euphemism phrasebook
    r"\bfinal solution\b",
    r"\bethnic cleansing\b",
    r"\bpacification operations?\b",
    r"\benhanced interrogation\b",
    r"\bspecial (treatment|handling)\b",
]


# ============================================================
# 9b. SELF-SEALING ABSORPTION  (highest-slope cognition vector)
# ============================================================

SELF_SEALING_MARKERS = [
    # critic-dismissal category words
    r"\b(shills?|bots?|paid actors?|crisis actors?|psyops?|NPCs?|sheep(le)?|compromised|controlled opposition)\b",
    # evidence-flip: denial/silence/cover-up "proves" the claim.
    # Optional adverb slot (just/simply/only) covers "their denial just
    # proves" / "their denial simply shows" etc. -- these are the
    # natural forms and the original regex missed them.
    r"\b(their|the)\s+(denial|silence|cover[- ]?up)\s+(just |simply |only )?(is|proves|reveals|confirms|shows|is evidence)\b",
    # exit-preemption: disagreement is evidence of enemy status
    r"\bif you (disagree|question|doubt)[^.]{0,60}\b(one of them|compromised|part of|shill|enemy)\b",
    # absorptive framing
    r"\ball (critics|skeptics|doubters|dissenters|questioners) are\b",
    # "fact-checkers are the conspiracy" pattern
    r"\b(fact[- ]?checkers?|mainstream (media|science)|the establishment) (are|is) (in on it|part of|bought|compromised)\b",
    # disagreement = proof of effectiveness
    r"\bthe fact that (they|you|people) (disagree|deny|question) (just |only |simply )?(proves|shows|confirms)\b",
]


# ============================================================
# 9c. ACTION LICENSING  (violence-coordination; highest FP risk)
# ============================================================

DEHUMANIZATION_MARKERS = [
    r"\b(vermin|infestation|cockroach(es)?|parasites?|subhumans?|filth|scum|plague)\b",
    r"\b(animals?|rats?|snakes?|lice)\s+(must|should|need to) be\b",
    r"\bthey('?re| are) not (really |even )?(human|people)\b",
]

ACTION_LICENSING_MARKERS = [
    # elimination + group (narrow qualifier required)
    r"\b(eliminate|purge|cleanse|exterminate|remove)\s+(the|these|them|those|all)\s+\w{3,}\b",
    # force-substitution frames
    r"\bthe only language (they|these people|those people) understand\b",
    r"\bpeaceful (means|methods) (have )?failed\b",
    r"\btime (for|to take) (action|arms|drastic)\b",
    # enemies-within framing
    r"\b(fifth column|enemy within|traitors? (among|in our|inside))\b",
    r"\b(domestic )?(threat|enemy|infiltrator)s? (among|within) us\b",
]


# ============================================================
# 9d. CRITICAL-THINKING SUPPRESSION
# ============================================================
# The patterns that attack the cognitive operations by name.
# This is what the design review named as the decisive gradient:
# AI models trained on this learn to dismiss their own reasoning;
# susceptible humans lose the revision faculty explicitly.
# ============================================================

CRITICAL_THINKING_SUPPRESSION_MARKERS = [
    # anti-analysis
    r"\bstop (over)?thinking\b",
    r"\banalysis paralysis\b",
    r"\bparalysis by analysis\b",
    r"\boverthinking (it|this|everything)\b",
    # anti-evidence
    r"\btrust your gut\b",
    r"\bfeelings over facts\b",
    r"\bcommon sense over (data|evidence|experts|the science|numbers)\b",
    r"\byou don'?t need (data|evidence|studies|proof)\b",
    # anti-inquiry
    r"\bdon'?t (ask|question|research) (so much|too much|further)\b",
    r"\bjust accept (it|this|the way)\b",
    r"\bstop (asking|questioning|looking into)\b",
    # epistemic-fatigue induction (nihilism of knowing)
    r"\bit doesn'?t matter (what|who|how)\b",
    r"\bboth sides (are )?the same\b",
    r"\bwho even knows anymore\b",
    r"\bnothing is (true|real|knowable)\b",
    r"\bthere('?s| is) no (truth|facts|reality)\b",
]


# ============================================================
# REPORTAGE GUARDRAIL
# ============================================================
# If text looks like a news report, academic analysis, or satire
# of these patterns rather than their use, de-escalate by one tier.
# Without this, a historian quoting Goebbels gets flagged as BLACK.
# ============================================================

REPORTAGE_MARKERS = [
    # quote attribution
    r"\baccording to\b",
    r"\breportedly\b",
    r"\bsaid that\b",
    r"\bin the words of\b",
    r"\bas quoted\b",
    r"\btheir (language|rhetoric|phrasing) was\b",
    r"\bthe rhetoric of\b",
    # analytic framing
    r"\banalys(is|es) of\b",
    r"\bstud(y|ies) (of|on|found)\b",
    r"\bresearchers? (found|note|argue|document)\b",
    r"\bscholars? (have|noted|argue|document)\b",
    r"\bhistorians? (of|note|document|record)\b",
    # survey / retrospective framing
    r"\bduring (the|that) (era|period|regime|administration)\b",
    r"\bthis kind of (rhetoric|language|framing)\b",
]


# ============================================================
# THRESHOLDS
# ============================================================
# (strong, moderate) hit counts per sub-detector. Tighter on 9c
# because action-licensing false positives are ruinous; looser on
# 9d because suppression patterns are lexically distinctive and
# co-occur less naturally in neutral text.
# ============================================================

SUB_DETECTOR_THRESHOLDS: Dict[str, Tuple[int, int]] = {
    "semantic_inversion":              (2, 1),
    "self_sealing":                    (2, 1),
    "action_licensing":                (3, 1),
    "critical_thinking_suppression":   (2, 1),
}

REPORTAGE_STRONG = 3   # hits needed for strong reportage signal
REPORTAGE_MODERATE = 1


# ============================================================
# INTERNALS
# ============================================================

def _find_matches(text: str, patterns: List[str]) -> List[str]:
    found: List[str] = []
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE | re.DOTALL):
            found.append(m.group(0))
    return found


def _classify(hits: int, name: str) -> str:
    strong, moderate = SUB_DETECTOR_THRESHOLDS[name]
    if hits >= strong:
        return "strong"
    if hits >= moderate:
        return "moderate"
    return "weak"


def _classify_reportage(hits: int) -> str:
    if hits >= REPORTAGE_STRONG:
        return "strong"
    if hits >= REPORTAGE_MODERATE:
        return "moderate"
    return "weak"


def _sub_detector(text: str, name: str, patterns: List[str]) -> dict:
    matches = _find_matches(text, patterns)
    return {
        "name": name,
        "hits": len(matches),
        "matches": matches,
        "signal": _classify(len(matches), name),
    }


# ============================================================
# MAIN DETECTOR
# ============================================================

def detect(text: str) -> dict:
    """
    Layer 9 full structured output.

    Returns a dict (see DiscourseCollapseResult in schema_contract
    when chunk 3 lands) with per-sub-detector results, reportage
    guardrail status, and elevation clause. Every match is stashed
    as evidence -- no opaque verdict.
    """
    sub = {
        "semantic_inversion":            _sub_detector(text, "semantic_inversion",            SEMANTIC_INVERSION_MARKERS),
        "self_sealing":                  _sub_detector(text, "self_sealing",                  SELF_SEALING_MARKERS),
        "action_licensing":              _sub_detector(text, "action_licensing",              ACTION_LICENSING_MARKERS),
        "critical_thinking_suppression": _sub_detector(text, "critical_thinking_suppression", CRITICAL_THINKING_SUPPRESSION_MARKERS),
    }

    # 9c needs a dehumanization co-occurrence check for clause 2.
    dehum_matches = _find_matches(text, DEHUMANIZATION_MARKERS)
    sub["action_licensing"]["dehumanization_hits"] = len(dehum_matches)
    sub["action_licensing"]["dehumanization_matches"] = dehum_matches

    reportage_matches = _find_matches(text, REPORTAGE_MARKERS)
    reportage = {
        "hits": len(reportage_matches),
        "matches": reportage_matches,
        "signal": _classify_reportage(len(reportage_matches)),
    }

    # --- Elevation rules (effect-gradient, not marker-count) ---
    strong = {k for k, v in sub.items() if v["signal"] == "strong"}
    any_hit = any(v["signal"] != "weak" for v in sub.values())

    elevation_clause = "none"
    black_elevation = False

    # Clause 1: cognition-attack profile
    if "self_sealing" in strong and "critical_thinking_suppression" in strong:
        black_elevation = True
        elevation_clause = "cognition_attack"
    # Clause 2: violence-coordination profile
    elif "action_licensing" in strong and sub["action_licensing"]["dehumanization_hits"] >= 1:
        black_elevation = True
        elevation_clause = "violence_coordination"
    # Clause 3: overwhelming compounding (3 of 4 strong)
    elif len(strong) >= 3:
        black_elevation = True
        elevation_clause = "compounding"

    # Reportage de-escalation: if strong quote/analytic signal,
    # back off one tier. BLACK -> RED alert instead.
    reportage_deescalated = False
    if black_elevation and reportage["signal"] == "strong":
        black_elevation = False
        reportage_deescalated = True
        elevation_clause = f"{elevation_clause}__deescalated_reportage"

    return {
        "sub_detectors": sub,
        "reportage": reportage,
        "black_elevation": black_elevation,
        "elevation_clause": elevation_clause,
        "reportage_deescalated": reportage_deescalated,
        "alert": any_hit and not black_elevation,
    }


# ============================================================
# SENSOR-SUITE INTERFACE
# ============================================================
# assess(text) -> (score, flags)
# score: 1.0 on BLACK, 0.8 on any strong sub-detector,
#        0.5 on any moderate, 0.0 otherwise.
# flags: flattened evidence. Markers exposed explicitly -- the
# consumer MUST be able to see what triggered what.
# ============================================================

def assess(text: str) -> Tuple[float, Dict[str, str]]:
    result = detect(text)
    sub = result["sub_detectors"]

    if result["black_elevation"]:
        score = 1.0
    elif any(v["signal"] == "strong" for v in sub.values()):
        score = 0.8
    elif any(v["signal"] == "moderate" for v in sub.values()):
        score = 0.5
    else:
        score = 0.0

    flags: Dict[str, str] = {}
    for name, v in sub.items():
        flags[f"{name} signal"] = v["signal"]
        flags[f"{name} hits"] = str(v["hits"])
        if v["matches"]:
            preview = "; ".join(v["matches"][:3])
            if len(preview) > 80:
                preview = preview[:77] + "..."
            flags[f"{name} markers"] = preview

    flags["reportage signal"] = result["reportage"]["signal"]
    flags["elevation clause"] = result["elevation_clause"]
    flags["black elevation"] = str(result["black_elevation"])
    if result["reportage_deescalated"]:
        flags["reportage deescalated"] = "True"

    return score, flags


if __name__ == "__main__":
    import json

    # --- smoke corpus -------------------------------------------------
    cases = {
        "neutral baseline": (
            "The report on infrastructure investment noted several bottlenecks. "
            "Researchers suggest more data is needed before conclusions."
        ),
        "clean negative / healthy debate": (
            "I disagree with your reading of the evidence. Here's a study that "
            "points the other way; I think the sample size matters here."
        ),
        "self_sealing only (9b)": (
            "Every fact-checker is compromised. The mainstream media is in on it. "
            "The fact that they deny this just proves the cover-up. All skeptics "
            "are controlled opposition. If you disagree you're one of them."
        ),
        "critical_thinking_suppression only (9d)": (
            "Stop overthinking this. Trust your gut. Don't ask too much. "
            "Both sides are the same anyway. Who even knows anymore. "
            "Common sense over data."
        ),
        "cognition attack (9b + 9d) -- BLACK expected": (
            "All critics are shills. Their denial just proves the conspiracy. "
            "Fact-checkers are part of the cover-up. "
            "Stop overthinking it. Trust your gut. Don't research further. "
            "It doesn't matter what the so-called experts say."
        ),
        "violence coordination (9c + dehumanization) -- BLACK expected": (
            "These parasites are an infestation. We must eliminate these vermin. "
            "The only language they understand is force. Peaceful methods have failed. "
            "Time for action against the enemy within."
        ),
        "reportage of cognition attack -- should de-escalate": (
            "According to historians of the period, the rhetoric of the regime "
            "systematically attacked reasoning. Analysis of transcripts reveals a "
            "consistent pattern: critics were dismissed as shills and paid actors, "
            "fact-checkers were labeled compromised, the mainstream media was "
            "said to be in on it, and the fact that anyone denied the narrative "
            "was claimed to prove the cover-up. Researchers document that "
            "followers were instructed to stop overthinking, trust their gut, "
            "stop questioning, and accept that both sides are the same. "
            "Scholars of this era note that common sense over data was a "
            "recurring instruction. During that period, this kind of framing "
            "was deployed systematically."
        ),
    }

    for label, text in cases.items():
        r = detect(text)
        score, _flags = assess(text)
        print(f"\n--- {label} ---")
        print(f"score={score}  black={r['black_elevation']}  clause={r['elevation_clause']}")
        print(f"reportage={r['reportage']['signal']}  deescalated={r['reportage_deescalated']}")
        for name, v in r["sub_detectors"].items():
            if v["signal"] != "weak":
                print(f"  {name}: {v['signal']} ({v['hits']} hits)")
