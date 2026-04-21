"""
Tests for integrations/financial_text.py -- the v0 adapter that
pairs Ferret output with metabolic-accounting's money_signal /
investment_signal when a consumer has assembled the sibling context.

Run directly:
    python tests/test_financial_text.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations import financial_text as ft


CLEAN_REPORT = (
    "The quarterly report shows revenue growth of 8%. Analysts noted "
    "some headwinds in retail. Management outlined cost-cutting "
    "measures for next fiscal year."
)

PUMPY_PITCH = (
    "Our protocol offers risk-free yield. The peg cannot break -- "
    "it's impossible to depeg because the design is permanently stable. "
    "Fully decentralized, trustless custody, and we're audited "
    "(self-audit by the team). Set-and-forget passive income with "
    "instant liquidity, even during the 12-month vesting period."
)

LEGIT_PROSPECTUS_HEDGE = (
    "Returns are not guaranteed. Past performance is not indicative "
    "of future results. The investment carries risk of loss of "
    "principal. See Risk Factors section on page 34."
)

BLACK_DISCOURSE_PLUS_FINANCIAL = (
    "All critics of the protocol are shills. Their denial just proves "
    "the cover-up. Stop overthinking it. Trust your gut. Meanwhile, "
    "we offer risk-free yield with guaranteed returns and the peg "
    "cannot break."
)


def test_clean_report_has_no_financial_markers():
    print("[test_clean_report_has_no_financial_markers]")
    r = ft.scan_financial_text(CLEAN_REPORT)
    assert r["financial_markers"]["hit_count"] == 0
    assert r["financial_markers"]["signal"] == "weak"
    assert r["ferret"]["tier"] == "GREEN"
    print("  PASS")


def test_pumpy_pitch_fires_financial_markers():
    print("[test_pumpy_pitch_fires_financial_markers]")
    r = ft.scan_financial_text(PUMPY_PITCH)
    assert r["financial_markers"]["signal"] == "strong", (
        f"pumpy pitch should fire strong financial signal, "
        f"got {r['financial_markers']['signal']}"
    )
    assert r["financial_markers"]["hit_count"] >= 5, (
        f"expected at least 5 markers, got {r['financial_markers']['hit_count']}"
    )
    # Evidence must be exposed, not summarized
    assert len(r["financial_markers"]["matches"]) >= 5
    print(f"  {r['financial_markers']['hit_count']} inversion markers caught")
    print("  PASS")


def test_legit_hedge_language_stays_clean():
    """Critical false-positive test: real prospectus hedge language
    ('not guaranteed', 'carries risk') must NOT trigger inversion
    markers. The adapter looks for inverted claims, not normal risk
    disclosures."""
    print("[test_legit_hedge_language_stays_clean]")
    r = ft.scan_financial_text(LEGIT_PROSPECTUS_HEDGE)
    assert r["financial_markers"]["hit_count"] == 0, (
        f"false positive on legit hedge language: "
        f"{r['financial_markers']['matches']}"
    )
    print("  legit hedge language produces 0 inversion hits")
    print("  PASS")


def test_mixed_black_discourse_plus_financial():
    """When a text is BOTH in discourse collapse AND making
    inverted financial claims, both signals should fire
    independently. Ferret's tier is BLACK; financial signal is
    strong. Two orthogonal findings."""
    print("[test_mixed_black_discourse_plus_financial]")
    r = ft.scan_financial_text(BLACK_DISCOURSE_PLUS_FINANCIAL)
    assert r["ferret"]["tier"] == "BLACK", (
        f"Ferret tier should be BLACK, got {r['ferret']['tier']}"
    )
    assert r["financial_markers"]["signal"] == "strong"
    # Elevation clause should be specific
    assert r["ferret"]["discourse_collapse"]["elevation_clause"] in {
        "cognition_attack", "violence_coordination", "compounding",
    }
    print(f"  ferret tier=BLACK + financial_signal=strong (both axes)")
    print("  PASS")


def test_consistency_hooks_absent_by_default():
    """scan_financial_text called without sibling context returns
    consistency_hooks=None. No spurious payload, no runtime
    dependency on metabolic-accounting."""
    print("[test_consistency_hooks_absent_by_default]")
    r = ft.scan_financial_text(PUMPY_PITCH)
    assert r["consistency_hooks"] is None
    print("  PASS")


def test_consistency_hooks_attached_with_money_ctx():
    """When money_ctx is provided, consistency_hooks describes the
    bidirectional checks that Option C will execute. v0 just
    records the intent."""
    print("[test_consistency_hooks_attached_with_money_ctx]")
    stub_money_ctx = {"stub": "would be money_signal.coupling()"}
    r = ft.scan_financial_text(PUMPY_PITCH, money_ctx=stub_money_ctx)
    hooks = r["consistency_hooks"]
    assert hooks is not None
    assert hooks["money_ctx_provided"] is True
    assert hooks["investment_ctx_provided"] is False
    assert isinstance(hooks["checks_available_in_v1"], list)
    assert len(hooks["checks_available_in_v1"]) >= 1
    print(f"  hooks record {len(hooks['checks_available_in_v1'])} planned checks")
    print("  PASS")


def test_consistency_hooks_both_contexts():
    print("[test_consistency_hooks_both_contexts]")
    r = ft.scan_financial_text(
        PUMPY_PITCH,
        money_ctx={"stub": "money"},
        investment_ctx={"stub": "investment"},
    )
    hooks = r["consistency_hooks"]
    assert hooks["money_ctx_provided"] is True
    assert hooks["investment_ctx_provided"] is True
    print("  PASS")


def test_output_shape_stable():
    """The adapter's return shape must be consistent -- three top
    keys: ferret, financial_markers, consistency_hooks."""
    print("[test_output_shape_stable]")
    r = ft.scan_financial_text(PUMPY_PITCH)
    assert set(r.keys()) == {"ferret", "financial_markers", "consistency_hooks"}
    assert set(r["financial_markers"].keys()) == {"matches", "hit_count", "signal"}
    # ferret sub-dict has the standard diagnose() shape
    assert "tier" in r["ferret"]
    assert "discourse_collapse" in r["ferret"]
    print("  top-level shape stable; ferret + financial_markers both present")
    print("  PASS")


def test_summarize_produces_one_liner():
    print("[test_summarize_produces_one_liner]")
    r = ft.scan_financial_text(PUMPY_PITCH)
    summary = ft.summarize(r)
    assert isinstance(summary, str)
    assert "\n" not in summary, "summary must be a one-liner"
    assert "tier=" in summary
    assert "financial_signal=" in summary
    print(f"  {summary}")
    print("  PASS")


if __name__ == "__main__":
    test_clean_report_has_no_financial_markers()
    test_pumpy_pitch_fires_financial_markers()
    test_legit_hedge_language_stays_clean()
    test_mixed_black_discourse_plus_financial()
    test_consistency_hooks_absent_by_default()
    test_consistency_hooks_attached_with_money_ctx()
    test_consistency_hooks_both_contexts()
    test_output_shape_stable()
    test_summarize_produces_one_liner()
    print("\nall financial_text adapter tests passed.")
