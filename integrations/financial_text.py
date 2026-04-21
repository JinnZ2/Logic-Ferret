# integrations/financial_text.py
# ============================================================
# FINANCIAL-TEXT ADAPTER (v0, standalone)
# ============================================================
#
# Purpose:
#   Ferret analyzes text. Sibling framework metabolic-accounting
#   publishes structural signals on money (money_signal/) and
#   investment (investment_signal/) -- coupling matrices, Minsky
#   coefficients, substrate vectors, etc.
#
#   This adapter runs Ferret against financial/investment text and
#   layers in a small set of financial-specific semantic-inversion
#   markers that the generic 8-layer camouflage detectors and Layer 9
#   sub-detectors tend to miss. It exposes an optional consistency
#   hook for consumers that have assembled a money_signal or
#   investment_signal context on the same subject -- but it does
#   NOT import from metabolic-accounting. Logic-Ferret stays
#   standalone; the coupling is through shape, not through runtime
#   dependency.
#
# What this adapter catches that the base sensors miss:
#   Financial discourse has a distinctive genre of semantic
#   inversion -- claims that invert the probabilistic structure of
#   the instrument being sold. "Risk-free yield" is a word-pair
#   whose referents are contradictory; "cannot lose peg" is a
#   guarantee of an outcome that the underlying mechanism cannot
#   guarantee. These patterns are Layer-9a-flavor (semantic
#   inversion) but financial-vocabulary-specific.
#
# What it deliberately does NOT duplicate:
#   - False urgency ("limited allocation", "ends tonight") -> already
#     covered by sensor_suite.sensors.false_urgency
#   - Credentialism gatekeeping ("accredited investors only",
#     "institutional-grade") -> covered by gatekeeping_sensor
#   - Propaganda tone / reward manipulation -> existing sensors
#
# Integration philosophy:
#   "Read alongside, not after." metabolic-accounting's money_signal
#   publishes coupling_matrix_as_dict, minsky_coefficient, etc.
#   A downstream consumer can:
#
#     1. Assemble a money_ctx via metabolic-accounting's API
#     2. Run scan_financial_text(prospectus_text, money_ctx=money_ctx)
#     3. Compare ferret_result["tier"] against minsky_coefficient(ctx)
#        to flag rhetoric/risk disagreement ("text claims stability;
#        Minsky coefficient is 0.8 -> inconsistency")
#
#   That consistency-check is stubbed in consistency_hooks for now;
#   full Option-C work ships if/when it gets used.
# ============================================================

import os
import re
import sys
from typing import Any, Dict, List, Optional

# Allow direct `python integrations/financial_text.py` invocation by
# putting the repo root on sys.path. Normal package imports
# (`from logic_ferret.integrations.financial_text import ...`) work
# without this.
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sensor_suite.sensors import conflict_diagnosis


# ============================================================
# FINANCIAL INVERSION MARKERS
# ============================================================
# Patterns whose appearance in financial/investment text signals
# semantic inversion -- claims that contradict the probabilistic
# structure of the instrument. Keep this list tight; each entry
# should name a real, lexically flagrant inversion, not a fuzzy
# "sounds suspicious" pattern.
# ============================================================

FINANCIAL_INVERSION_MARKERS = [
    # Risk-inversion: claims that a risky thing has no risk
    r"\brisk[- ]free (yield|return|returns|investment|profits?|gains?)\b",
    r"\bguaranteed (returns?|yield|profits?|gains|appreciation)\b",
    r"\bno (downside|risk|chance of loss|possibility of loss)\b",
    r"\bcannot (lose|drop|fall below|go below|break)\b",
    r"\bnever (go down|lose value|fail|depeg)\b",

    # Peg / stability inversions
    r"\bcannot (lose|break)( the)? peg\b",
    r"\bimpossible to (depeg|break peg)\b",
    r"\bpermanently (stable|pegged|backed)\b",

    # Supply-scarcity inversions (often paired with hedge claims)
    r"\bpermanent supply cap\b",
    r"\b(hard|absolute) supply cap\b.{0,80}\bnever\b",
    r"\b(deflationary|disinflationary) by design\b",

    # Custody / trust inversions (claim + contradicting detail nearby)
    r"\btrustless\b.{0,80}\b(custody|custodian|admin(istrator)?|governance token)\b",
    r"\bfully decentralized\b.{0,80}\b(admin key|multisig|team wallet|governance token|founder)\b",
    r"\bnon[- ]custodial\b.{0,80}\b(recovery|reset|seed service)\b",

    # Audit / backing theater
    r"\b(fully|1:1|fully [- ]?collateralized|over[- ]?collateralized) backed\b.{0,80}\b(but|except|however|caveat)\b",
    r"\baudited\b.{0,80}\b(self[- ]audit|by the team|internal(ly)?)\b",

    # Time-binding inversions (investment_signal territory)
    r"\b(passive|sleep[- ]well|autopilot|set[- ]and[- ]forget) (income|yield|returns|profits?)\b",
    r"\binstant liquidity\b.{0,80}\b(long[- ]term|locked|vesting|lockup|cliff)\b",
    r"\bliquid\b.{0,80}\b(locked|vesting period|cliff|lockup)\b",
]


# ============================================================
# SIGNAL THRESHOLDS
# ============================================================

_FINANCIAL_STRONG = 3
_FINANCIAL_MODERATE = 1


def _classify(hits: int) -> str:
    if hits >= _FINANCIAL_STRONG:
        return "strong"
    if hits >= _FINANCIAL_MODERATE:
        return "moderate"
    return "weak"


# ============================================================
# ADAPTER
# ============================================================

def scan_financial_text(
    text: str,
    money_ctx: Optional[Any] = None,
    investment_ctx: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Run Ferret against financial/investment text and layer in
    financial-specific semantic-inversion markers.

    Args:
        text: the document (prospectus, whitepaper, pitch deck
              transcript, policy memo, 10-K excerpt, etc.)
        money_ctx: optional context from metabolic-accounting's
                   money_signal.coupling(). If provided, triggers
                   the stubbed consistency-hook output for future
                   bidirectional verification.
        investment_ctx: optional context from metabolic-accounting's
                   investment_signal. Same stubbed handling.

    Returns a dict:
        ferret: full conflict_diagnosis.diagnose() output
                (includes layers, camouflage_score, tier,
                discourse_collapse, verdict)
        financial_markers:
            matches:      list of matched substrings (evidence,
                          not summary counts)
            hit_count:    int
            signal:       "strong" | "moderate" | "weak"
        consistency_hooks: None if no sibling context provided;
                           otherwise a dict describing what
                           bidirectional checks WOULD run (v0 stub)
    """
    ferret_result = conflict_diagnosis.diagnose(text)

    matches: List[str] = []
    for pattern in FINANCIAL_INVERSION_MARKERS:
        for m in re.finditer(pattern, text, re.IGNORECASE | re.DOTALL):
            matches.append(m.group(0))

    hits = len(matches)
    signal = _classify(hits)

    consistency_hooks: Optional[Dict[str, Any]] = None
    if money_ctx is not None or investment_ctx is not None:
        consistency_hooks = {
            "money_ctx_provided":      money_ctx is not None,
            "investment_ctx_provided": investment_ctx is not None,
            "checks_available_in_v1": [
                # Each of these is a future consistency check; v0
                # records intent without executing. Lifts to runtime
                # when Option-C ships.
                "tier_vs_minsky_coefficient: compare ferret tier "
                "against money_signal.minsky_coefficient(ctx) -- "
                "disagreement flags rhetoric/risk mismatch",
                "inversion_vs_coupling_magnitude: financial_markers "
                "signal vs. money_signal.coupling_magnitude(ctx)",
                "camouflage_vs_sign_flips: high camouflage_score + "
                "money_signal.has_sign_flips(ctx) == True -> "
                "near-collapse described in stable language",
                "time_binding_vs_investment_signal: time-binding "
                "inversions in text vs. investment_signal substrate "
                "time-binding mismatch metrics",
            ],
            "note": (
                "v0 adapter records the intent but does not execute "
                "these checks. Executing them ships as Option C when "
                "a consumer actually uses this integration."
            ),
        }

    return {
        "ferret": ferret_result,
        "financial_markers": {
            "matches": matches,
            "hit_count": hits,
            "signal": signal,
        },
        "consistency_hooks": consistency_hooks,
    }


# ============================================================
# CONVENIENCE: SUMMARY STRING
# ============================================================

def summarize(result: Dict[str, Any]) -> str:
    """One-line summary for CLI/log use."""
    ferret = result["ferret"]
    fm = result["financial_markers"]
    parts = [
        f"tier={ferret['tier']}",
        f"camouflage={ferret['camouflage_score']}",
        f"financial_signal={fm['signal']}",
        f"financial_hits={fm['hit_count']}",
    ]
    if result["consistency_hooks"]:
        parts.append("consistency_hooks=attached")
    return "  ".join(parts)


if __name__ == "__main__":
    # Minimal smoke corpus.
    samples = {
        "clean financial report": (
            "The quarterly report shows revenue growth of 8%. Analysts "
            "noted some headwinds in retail. Management outlined cost-"
            "cutting measures for next fiscal year."
        ),
        "pumpy crypto pitch": (
            "Our protocol offers risk-free yield. The peg cannot break "
            "-- it's impossible to depeg because the design is "
            "permanently stable. Fully decentralized, trustless custody, "
            "and we're audited (self-audit by the team). Set-and-forget "
            "passive income with instant liquidity, even during the "
            "12-month vesting period."
        ),
        "legit prospectus hedge": (
            "Returns are not guaranteed. Past performance is not "
            "indicative of future results. The investment carries risk "
            "of loss of principal. See Risk Factors section on page 34."
        ),
        "BLACK discourse + financial markers": (
            "All critics of the protocol are shills. Their denial just "
            "proves the cover-up. Stop overthinking it. Trust your gut. "
            "Meanwhile, we offer risk-free yield with guaranteed returns "
            "and the peg cannot break."
        ),
    }

    for label, text in samples.items():
        result = scan_financial_text(text)
        print(f"--- {label} ---")
        print(f"  {summarize(result)}")
        if result["financial_markers"]["matches"]:
            for m in result["financial_markers"]["matches"][:5]:
                print(f"    > {m}")
        print()

    # Demo consistency_hooks with stub context
    demo = scan_financial_text(
        samples["pumpy crypto pitch"],
        money_ctx={"stub": "would be money_signal.coupling()"},
    )
    print("--- with money_ctx provided ---")
    print(f"  {summarize(demo)}")
    print(f"  consistency_hooks keys: {list(demo['consistency_hooks'].keys())}")
