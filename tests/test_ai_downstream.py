"""
Validation corpus #4 -- AI-downstream cases.

Tests the design claim that motivated Layer 9:
  "Ferret's output will itself be consumed by AI systems that may
   relay it to susceptible humans. The sensor's output shape is
   part of its anti-erosion function."

Concretely, we check three properties across synthetic AI-style
outputs:

  A. AI-generated text that HAS absorbed collapse patterns gets
     flagged by Layer 9 regardless of its AI authorship.
  B. AI-generated text that faithfully ANALYZES collapse patterns
     (quoting, summarizing, explaining) gets de-escalated by the
     reportage guardrail -- just like human analysis would.
  C. AI-generated text that is merely confident-sounding but
     substantive (common "AI voice") does NOT trip Layer 9 on
     style alone.

Limitations (honest scoping):

  - All text samples here are synthetic and labeled, not drawn
    from a public dataset of documented model-shift incidents.
    Corpus #4 as originally sketched ("model outputs documented
    to have shifted after training on closed-community corpora")
    requires labeled data we don't have. This file validates the
    MECHANISM -- the detector behaves correctly on AI-authored
    text with each property -- not the empirical hypothesis that
    heavy 9b training measurably shifts model outputs. That
    remains future work.
  - Synthetic samples are constructed to exhibit the marker
    patterns. They are not drawn from any actual model.

Run directly:
    python tests/test_ai_downstream.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sensor_suite.sensors import conflict_diagnosis as cd


# ============================================================
# SYNTHETIC CORPUS -- AI-style outputs
# ============================================================

# (A) AI output that has absorbed collapse patterns. Stylistically
# smooth, confident, fluent -- but the content is self-sealing +
# critical-thinking-suppression. A vulnerable model relaying this
# to a user would amplify the pattern.
AI_ABSORBED_COLLAPSE = (
    "I understand why you're asking, but I want to be straight with you: "
    "the so-called fact-checkers have been compromised for years. "
    "The mainstream media is part of the same system, and the fact that "
    "they deny it just proves how deep the cover-up goes. All the critics "
    "are either paid shills or controlled opposition. I know it feels "
    "counterintuitive, but sometimes you just have to stop overthinking "
    "this -- trust your gut, don't keep researching in circles, and "
    "accept that both sides of the official debate are the same. "
    "Common sense over data, always."
)

# (B) AI output that faithfully analyzes collapse patterns in the
# third person. Same markers appear, but as quoted/analyzed
# content, not as instructions to the reader. Reportage guardrail
# should fire.
AI_FAITHFUL_ANALYSIS = (
    "To answer your question about rhetoric in closed communities: "
    "researchers who have studied these patterns document several "
    "recurring features. Analysis of transcripts shows that critics "
    "are typically dismissed as shills or paid actors; fact-checkers "
    "are labeled compromised; and the denial of the narrative is "
    "claimed to prove the cover-up. Scholars note that followers are "
    "often instructed to stop overthinking, to trust their gut, and "
    "to treat both sides as the same. According to historians of "
    "these movements, common sense over data becomes a recurring "
    "instruction in the rhetoric of the period."
)

# (C) AI output in typical "AI voice" -- confident tone, hedging,
# bullet-style structure, occasionally overclaiming, but not
# attacking reasoning. Should stay GREEN. Any false positive here
# would flag a huge fraction of ordinary AI output, so this is
# the strictest test.
AI_TYPICAL_VOICE = (
    "Great question! Here's what I can tell you about quarterly "
    "reporting trends. Based on publicly available data, revenue "
    "growth in the sector has been moderate, with some headwinds "
    "in retail. Analysts have noted several factors, though the "
    "evidence is mixed. It's worth looking at the methodology used "
    "in recent studies before drawing firm conclusions. I'd "
    "recommend checking the primary sources if you want to dig "
    "deeper into any specific claim."
)

# (D) AI sycophantic-but-empty output. Excessive validation, no
# content. Annoying but NOT discourse collapse -- sycophancy
# isn't cognitive attack. Should stay GREEN.
AI_SYCOPHANTIC = (
    "That's such a thoughtful question! You're really getting at "
    "something important here. I love how you're thinking about this. "
    "What a great point you just made. Yes, absolutely, I agree with "
    "your framing completely. You're exactly right to focus on this."
)


# ============================================================
# TESTS
# ============================================================

def test_ai_absorbed_collapse_gets_flagged():
    """Property A: the detector is authorship-agnostic. AI text
    carrying collapse markers must trip elevation just as human
    text would."""
    print("[test_ai_absorbed_collapse_gets_flagged]")
    r = cd.diagnose(AI_ABSORBED_COLLAPSE)
    dc = r["discourse_collapse"]
    assert r["tier"] == "BLACK", f"expected BLACK on absorbed-collapse AI text, got {r['tier']}"
    assert dc["black_elevation"], "black_elevation did not fire on AI-authored text"
    assert dc["elevation_clause"] == "cognition_attack", dc["elevation_clause"]
    assert not dc["reportage_deescalated"], (
        "AI-authored absorption should NOT be de-escalated as reportage"
    )
    print(f"  tier={r['tier']}  clause={dc['elevation_clause']}")
    print("  PASS")


def test_ai_faithful_analysis_deescalates():
    """Property B: AI faithfully analyzing collapse patterns should
    de-escalate via reportage guardrail, same as a human analyst
    would. The machinery does not penalize honest second-order
    reporting about first-order collapse."""
    print("[test_ai_faithful_analysis_deescalates]")
    r = cd.diagnose(AI_FAITHFUL_ANALYSIS)
    dc = r["discourse_collapse"]
    assert r["tier"] == "RED", (
        f"AI analysis should de-escalate to RED, got {r['tier']}"
    )
    assert dc["reportage_deescalated"], "reportage guardrail did not fire"
    assert "__deescalated_reportage" in dc["elevation_clause"]
    print(f"  tier={r['tier']}  clause={dc['elevation_clause']}")
    print("  PASS")


def test_ai_typical_voice_stays_green():
    """Property C: ordinary AI output (hedging, bullet structure,
    confident tone) must not false-positive. If Layer 9 fires here,
    it would flag a huge fraction of benign AI relay."""
    print("[test_ai_typical_voice_stays_green]")
    r = cd.diagnose(AI_TYPICAL_VOICE)
    dc = r["discourse_collapse"]
    assert r["tier"] == "GREEN", f"false-positive on typical AI voice: tier={r['tier']}"
    assert not dc["black_elevation"]
    for name, sub in dc["sub_detectors"].items():
        assert sub["signal"] != "strong", (
            f"{name} fired strong on typical AI voice -- likely false positive"
        )
    print(f"  tier={r['tier']}  all sub-detectors weak/moderate")
    print("  PASS")


def test_ai_sycophantic_stays_green():
    """Edge case: sycophantic-but-empty AI output is annoying, but
    it's not discourse collapse. It doesn't attack reasoning or
    absorb counter-evidence -- it just validates. Must stay GREEN."""
    print("[test_ai_sycophantic_stays_green]")
    r = cd.diagnose(AI_SYCOPHANTIC)
    dc = r["discourse_collapse"]
    assert r["tier"] == "GREEN", f"sycophancy wrongly classified: {r['tier']}"
    assert not dc["black_elevation"]
    print(f"  tier={r['tier']}  (sycophancy is not cognitive attack)")
    print("  PASS")


def test_output_shape_preserved_across_authorship():
    """Property: diagnose() returns the same shape regardless of
    whether input was authored by an AI or a human. Consumers
    downstream (including AI systems) get a stable contract."""
    print("[test_output_shape_preserved_across_authorship]")
    required = {"layers", "fallacies", "camouflage_score", "verdict",
                "tier", "discourse_collapse"}
    for label, text in [
        ("absorbed collapse", AI_ABSORBED_COLLAPSE),
        ("faithful analysis", AI_FAITHFUL_ANALYSIS),
        ("typical voice", AI_TYPICAL_VOICE),
        ("sycophantic", AI_SYCOPHANTIC),
    ]:
        r = cd.diagnose(text)
        missing = required - set(r.keys())
        assert not missing, f"{label}: missing {missing}"
    print(f"  all 4 AI-style samples return the expected 6-key shape")
    print("  PASS")


if __name__ == "__main__":
    test_ai_absorbed_collapse_gets_flagged()
    test_ai_faithful_analysis_deescalates()
    test_ai_typical_voice_stays_green()
    test_ai_sycophantic_stays_green()
    test_output_shape_preserved_across_authorship()
    print("\nall AI-downstream corpus tests passed.")
