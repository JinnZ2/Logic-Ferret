# schema_contract.py
# ============================================================
# LOGIC-FERRET SCHEMA CONTRACT
# The declared stable surface. TAF's ferret_fieldlink mirrors this.
# ============================================================
#
# If you consume Logic-Ferret from another project, import from here.
# Everything in this file is covered by a versioning promise:
#
#   SCHEMA_VERSION = "MAJOR.MINOR.PATCH"
#     MAJOR -- rename / remove / shape change      (breaking)
#     MINOR -- new sensor / new flag key added     (additive)
#     PATCH -- docstring, typo, internal cleanup   (safe)
#
# Anything outside this file is internal. No promises.
#
# Sibling Framework:
#   Thermodynamic Accountability Framework (TAF)
#   https://github.com/JinnZ2/thermodynamic-accountability-framework
#   TAF's ferret_fieldlink.py calls ferret_surface() to introspect
#   this contract and keep the two frameworks in lockstep.
# ============================================================

from typing import Any, Callable, Dict, List, Tuple, TypedDict

from sensor_suite.sensors import (
    agency_detector,
    conflict_diagnosis,
    discourse_collapse,
    fallacy_overlay,
    false_urgency,
    gaslight_frequency_meter,
    gatekeeping_sensor,
    logic_fallacy_ferret,
    meritocracy_detector,
    narrative_fragility,
    propaganda_bias,
    propaganda_tone,
    responsibility_deflection_sensor,
    reward_manipulation,
    true_accountability_sensor,
    truth_integrity_score,
)

SCHEMA_VERSION = "1.2.0"


# ------------------------------------------------------------
# Sensor interface
# ------------------------------------------------------------
# Every module in SENSOR_REGISTRY exports:
#     assess(text: str) -> (score, flags)
#         score: float in [0.0, 1.0]; higher = more of what the
#                sensor measures (camouflage, manipulation, etc.)
#         flags: Dict[str, Any]; keys are stable per sensor.
#                Values are typically str (formatted) or int.
# ------------------------------------------------------------

SensorScore = float
SensorFlags = Dict[str, Any]
AssessFn = Callable[[str], Tuple[SensorScore, SensorFlags]]

SENSOR_REGISTRY: Dict[str, AssessFn] = {
    "Propaganda Tone":           propaganda_tone.assess,
    "Reward Manipulation":       reward_manipulation.assess,
    "False Urgency":             false_urgency.assess,
    "Gatekeeping":               gatekeeping_sensor.assess,
    "Narrative Fragility":       narrative_fragility.assess,
    "Agency Score":              agency_detector.assess,
    "Propaganda Bias":           propaganda_bias.assess,
    "Logic Fallacy Ferret":      logic_fallacy_ferret.assess,
    "Gaslight Frequency":        gaslight_frequency_meter.assess,
    "Responsibility Deflection": responsibility_deflection_sensor.assess,
    "True Accountability":       true_accountability_sensor.assess,
    "Meritocracy Detector":      meritocracy_detector.assess,
    "Conflict Diagnosis":        conflict_diagnosis.assess,
    "Discourse Collapse":        discourse_collapse.assess,
}


# ------------------------------------------------------------
# Conflict diagnosis structured output
# ------------------------------------------------------------
# conflict_diagnosis.diagnose(text: str) -> DiagnoseResult
# Keys below are stable. Per-layer "extras" are optional and
# only present on layers that produce them.
# ------------------------------------------------------------

class LayerResult(TypedDict, total=False):
    layer: str
    hits: int
    matches: List[str]
    signal: str
    structural_hits: int
    performative_hits: int
    negative_hits: int
    positive_hits: int
    divergence: int


class SubDetectorResult(TypedDict, total=False):
    name: str
    hits: int
    matches: List[str]
    signal: str
    # action_licensing only:
    dehumanization_hits: int
    dehumanization_matches: List[str]


class ReportageResult(TypedDict):
    hits: int
    matches: List[str]
    signal: str


class DiscourseCollapseResult(TypedDict):
    sub_detectors: Dict[str, SubDetectorResult]  # keys drawn from DISCOURSE_COLLAPSE_MODES
    reportage: ReportageResult
    black_elevation: bool
    elevation_clause: str                         # see ELEVATION_CLAUSES
    reportage_deescalated: bool
    alert: bool                                   # markers fired but no elevation


class DiagnoseResult(TypedDict):
    layers: List[LayerResult]
    fallacies: Dict[str, int]
    camouflage_score: float
    verdict: str
    tier: str                                     # member of TIER_LEVELS
    discourse_collapse: DiscourseCollapseResult


LAYER_NAMES: Tuple[str, ...] = (
    "Stated Problem",
    "Feasibility Gap",
    "Incentive Mapping",
    "Systemic Alignment",
    "Consequence Analysis",
    "Hidden Driver",
    "Peripheral Signals",
    "Feedback Loops",
)

SIGNAL_LEVELS: Tuple[str, ...] = ("strong", "moderate", "weak")

DIAGNOSE: Callable[[str], DiagnoseResult] = conflict_diagnosis.diagnose


# ------------------------------------------------------------
# Fallacy overlay
# ------------------------------------------------------------
# fallacy_overlay.annotate_text(text) -> (annotated_str, counts)
# counts: {fallacy_name: int} over FALLACY_NAMES.
# ------------------------------------------------------------

FALLACY_NAMES: Tuple[str, ...] = tuple(fallacy_overlay.FALLACY_PATTERNS.keys())

ANNOTATE_TEXT: Callable[[str], Tuple[str, Dict[str, int]]] = (
    fallacy_overlay.annotate_text
)


# ------------------------------------------------------------
# Composite score
# ------------------------------------------------------------
# calculate_c3(scores: Dict[str, float])
#   -> (c3_score: float in [0.0, 1.0], weighted_breakdown: Dict[str, float])
# Keys of `scores` should be drawn from SENSOR_REGISTRY; unknown
# keys are accepted with a default weight of 1.0.
# ------------------------------------------------------------

CALCULATE_C3: Callable[[Dict[str, float]], Tuple[float, Dict[str, float]]] = (
    truth_integrity_score.calculate_c3
)


# ------------------------------------------------------------
# Tier taxonomy
# ------------------------------------------------------------
# Shared four-level vocabulary with the sibling frameworks
# (metabolic-accounting, TAF). String constants, not an enum --
# strings survive JSON, IPC, and cross-framework imports cleanly.
#
# Logic-Ferret emits GREEN, AMBER, or RED from its own data.
# BLACK is reserved: we have no physical irreversibility signal
# of our own (rhetoric isn't thermodynamically unrecoverable),
# so BLACK is only ever elevated into by a consumer that fuses
# Ferret output with an irreversibility source (e.g. TAF past-cliff
# basins). Defining it here keeps the vocabulary complete.
# ------------------------------------------------------------

GREEN = "GREEN"
AMBER = "AMBER"
RED   = "RED"
BLACK = "BLACK"

TIER_LEVELS: Tuple[str, ...] = (GREEN, AMBER, RED, BLACK)

# Per-layer signal ("strong"/"moderate"/"weak") -> Tier.
SIGNAL_TO_TIER: Dict[str, str] = {
    "strong":   RED,
    "moderate": AMBER,
    "weak":     GREEN,
}

# Thresholds over a [0.0, 1.0] score. Sorted high-to-low; the
# first threshold a score meets wins. Aligns with the existing
# VERDICTS cutoffs in conflict_diagnosis:
#     >= 0.70  HIGH CAMOUFLAGE    -> RED
#     >= 0.45  MODERATE           -> AMBER
#     <  0.45  LOW / MINIMAL      -> GREEN
CAMOUFLAGE_TIER_THRESHOLDS: Tuple[Tuple[float, str], ...] = (
    (0.70, RED),
    (0.45, AMBER),
    (0.00, GREEN),
)


def score_to_tier(score: float) -> str:
    """
    Map a [0.0, 1.0] score to a Tier string using
    CAMOUFLAGE_TIER_THRESHOLDS. Never returns BLACK -- consumers
    elevate to BLACK based on their own irreversibility signal.
    """
    for threshold, tier in CAMOUFLAGE_TIER_THRESHOLDS:
        if score >= threshold:
            return tier
    return GREEN


def layer_tiers(text: str) -> Dict[str, str]:
    """
    Per-layer Tier vector from one diagnose() pass.

    Returns {layer_name: Tier} over all 8 LAYER_NAMES. Collapsing
    this to the scalar camouflage_score loses which layer is hot;
    consumers that care about *where* the camouflage is (TAF
    cross-referencing Feasibility Gap vs Incentive Mapping) should
    read this instead of the composite score.
    """
    result = conflict_diagnosis.diagnose(text)
    return {lr["layer"]: SIGNAL_TO_TIER[lr["signal"]] for lr in result["layers"]}


# ------------------------------------------------------------
# Layer 9: Discourse Collapse
# ------------------------------------------------------------
# BLACK-tier sub-detectors and elevation clauses. Only Layer 9
# emits BLACK; the other 8 camouflage layers cap at RED.
#
# DISCOURSE_COLLAPSE_MODES are the sub-detector keys returned in
# DiscourseCollapseResult.sub_detectors.
#
# ELEVATION_CLAUSES are the possible values of elevation_clause.
# When the reportage guardrail fires, the clause is suffixed with
# REPORTAGE_DEESCALATED_SUFFIX (e.g. "cognition_attack__deescalated_reportage").
# ------------------------------------------------------------

DISCOURSE_COLLAPSE_MODES: Tuple[str, ...] = (
    "semantic_inversion",
    "self_sealing",
    "action_licensing",
    "critical_thinking_suppression",
)

ELEVATION_CLAUSES: Tuple[str, ...] = (
    "none",
    "cognition_attack",
    "violence_coordination",
    "compounding",
)

REPORTAGE_DEESCALATED_SUFFIX = "__deescalated_reportage"

DISCOURSE_COLLAPSE_DETECT: Callable[[str], DiscourseCollapseResult] = (
    discourse_collapse.detect
)


def sensor_tiers(text: str) -> Dict[str, str]:
    """
    Per-sensor Tier vector across SENSOR_REGISTRY.

    Runs every registered sensor once and maps its scalar score
    through score_to_tier. Lets a consumer see "Gaslight Frequency
    is RED, everything else GREEN" without the composite averaging
    it back into the noise floor.
    """
    tiers: Dict[str, str] = {}
    for name, fn in SENSOR_REGISTRY.items():
        score, _flags = fn(text)
        tiers[name] = score_to_tier(score)
    return tiers


# ------------------------------------------------------------
# Signatures
# ------------------------------------------------------------
# Stringified type signatures of every callable on the surface.
# Treated as part of the contract: any change here must bump
# SCHEMA_VERSION. Consumers can pin via assert_signatures().
# ------------------------------------------------------------

SIGNATURES: Dict[str, str] = {
    "assess": "(text: str) -> (float, Dict[str, Any])",
    "diagnose": (
        "(text: str) -> {layers, fallacies, camouflage_score, "
        "verdict, tier, discourse_collapse}"
    ),
    "annotate_text": "(text: str) -> (str, Dict[str, int])",
    "calculate_c3": "(Dict[str, float]) -> (float, Dict[str, float])",
    "score_to_tier": "(float) -> str",
    "layer_tiers": "(text: str) -> Dict[str, str]",
    "sensor_tiers": "(text: str) -> Dict[str, str]",
    "discourse_collapse_detect": "(text: str) -> DiscourseCollapseResult",
}


class SignatureMismatch(Exception):
    """Raised when a consumer's pinned signatures don't match this contract."""


def assert_signatures(expected: Dict[str, str]) -> None:
    """
    Fail loud if the consumer's pinned signatures have drifted from ours.

    TAF's ferret_fieldlink.py keeps its own SIGNATURES copy and calls this
    on import. Any drift -> SignatureMismatch, naming every offending key.
    """
    diffs = []
    for key, want in expected.items():
        got = SIGNATURES.get(key)
        if got is None:
            diffs.append(f"{key}: missing from contract (expected {want!r})")
        elif got != want:
            diffs.append(f"{key}: expected {want!r}, contract has {got!r}")
    if diffs:
        raise SignatureMismatch(
            f"Logic-Ferret schema {SCHEMA_VERSION} signature drift:\n  "
            + "\n  ".join(diffs)
        )


# ------------------------------------------------------------
# Introspection hook
# ------------------------------------------------------------

def ferret_surface() -> dict:
    """
    Plain-data snapshot of the contract.

    TAF's ferret_fieldlink.py calls this to validate it's speaking
    the right version before routing sensor scores between the
    two frameworks.
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "sensor_names": list(SENSOR_REGISTRY.keys()),
        "layer_names": list(LAYER_NAMES),
        "signal_levels": list(SIGNAL_LEVELS),
        "fallacy_names": list(FALLACY_NAMES),
        "tier_levels": list(TIER_LEVELS),
        "signal_to_tier": dict(SIGNAL_TO_TIER),
        "camouflage_tier_thresholds": [
            [threshold, tier] for threshold, tier in CAMOUFLAGE_TIER_THRESHOLDS
        ],
        "discourse_collapse_modes": list(DISCOURSE_COLLAPSE_MODES),
        "elevation_clauses": list(ELEVATION_CLAUSES),
        "reportage_deescalated_suffix": REPORTAGE_DEESCALATED_SUFFIX,
        "black_elevation_policy": (
            "BLACK is emitted only by Layer 9 (discourse_collapse). "
            "The other 8 camouflage layers cap at RED. "
            "Reportage guardrail de-escalates BLACK -> RED on strong "
            "quote/analytic framing, and suffixes the elevation_clause "
            "with reportage_deescalated_suffix."
        ),
        "signatures": dict(SIGNATURES),
    }


__all__ = [
    "SCHEMA_VERSION",
    "SENSOR_REGISTRY",
    "LAYER_NAMES",
    "SIGNAL_LEVELS",
    "FALLACY_NAMES",
    "SIGNATURES",
    "SignatureMismatch",
    "assert_signatures",
    "LayerResult",
    "SubDetectorResult",
    "ReportageResult",
    "DiscourseCollapseResult",
    "DiagnoseResult",
    "DIAGNOSE",
    "ANNOTATE_TEXT",
    "CALCULATE_C3",
    "DISCOURSE_COLLAPSE_DETECT",
    "GREEN", "AMBER", "RED", "BLACK",
    "TIER_LEVELS",
    "SIGNAL_TO_TIER",
    "CAMOUFLAGE_TIER_THRESHOLDS",
    "DISCOURSE_COLLAPSE_MODES",
    "ELEVATION_CLAUSES",
    "REPORTAGE_DEESCALATED_SUFFIX",
    "score_to_tier",
    "layer_tiers",
    "sensor_tiers",
    "ferret_surface",
]


if __name__ == "__main__":
    import json
    print(json.dumps(ferret_surface(), indent=2))
