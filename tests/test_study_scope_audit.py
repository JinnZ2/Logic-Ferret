"""
Tests for study_scope_audit -- the scope-bounded-measurement
reasoning framework.

Not a sensor; not an integration. A companion module that gives
AI systems (and humans) a structured audit to apply BEFORE citing
a study as evidence.

Run directly:
    python tests/test_study_scope_audit.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge.study_scope_audit import (
    Coupling, Regime, ScopeStatus,
    InstrumentAudit, ProtocolAudit, DomainCouplingAudit,
    RegimeAudit, CausalModelAudit, ScopeBoundary,
    StudyScopeAudit,
    HISTORICAL_CASES, PREMISE, AI_REASONING_RULE, META_INSIGHT,
)


# ============================================================
# FIXTURE: a synthetic study audit -- polymer fatigue in clean
# lab conditions. Picked because the scope failure mode is
# familiar (lab data != field conditions).
# ============================================================

def _build_audit(deployment_context=None) -> StudyScopeAudit:
    return StudyScopeAudit(
        claim="Polymer X exhibits 10^7 cycle fatigue life at 10 MPa stress",
        citation="Acme et al., 2023",
        instrument=InstrumentAudit(
            instrument_name="servo-hydraulic fatigue rig",
            physical_quantity_measured="tensile cyclic force",
            measurement_range=(0.1, 50.0),
            resolution=0.01,
            noise_floor=0.005,
            sampling_rate_hz=100.0,
            spatial_resolution=None,
            calibration_source="NIST-traceable load cell",
            calibration_traceability="NIST primary",
            drift_rate="0.1%/year",
        ),
        protocol=ProtocolAudit(
            sample_preparation="machined lab coupon, polished to Ra < 0.4 um",
            environmental_controls={"temp_C": 22, "humidity": 0.50},
            excluded_conditions=["UV exposure", "moisture cycling", "salt spray"],
            control_group_definition="unstressed coupon from same batch",
            measurement_duration="1000 hr",
            replication_count=5,
            blinding=False,
            pre_registration=False,
        ),
        coupling=DomainCouplingAudit(
            physical_domain="polymer mechanical engineering",
            instrument_coupling=Coupling.TIGHT,
            protocol_coupling=Coupling.TIGHT,
            substrate_coupling=Coupling.MODERATE,
            regime_coupling=Coupling.MODERATE,
        ),
        regime=RegimeAudit(
            assumed_baseline="stable polymer formulation, stable lab conditions",
            baseline_validity_window="2020-2024",
            regime_state=Regime.STATIONARY,
            regime_drift_indicators=[],
            extrapolation_horizon="5 years in similar conditions",
        ),
        causal_model=CausalModelAudit(
            causal_frame="mechanistic fatigue curve, stress-cycle relationship",
            confounders_identified=["temperature", "humidity", "stress ratio"],
            confounders_controlled=["temperature", "humidity"],
            confounders_unmeasured=["UV degradation", "chemical environment"],
            unknown_unknowns_acknowledged=True,
            alternative_frames_considered=["statistical Weibull", "crack-growth"],
        ),
        scope=ScopeBoundary(
            in_scope_conditions=["clean lab", "22C", "dry", "machined coupon"],
            edge_conditions=["outdoor lab", "40C", "50% humidity"],
            out_of_scope_conditions=[
                "marine environment", "UV exposure",
                "chemical contact", "field deployment",
            ],
            undeclared_scope=["sub-zero temperatures", "vacuum"],
            extrapolation_claims=[],
        ),
        deployment_context=deployment_context,
    )


# ============================================================
# TESTS
# ============================================================

def test_coupling_enum_complete():
    print("[test_coupling_enum_complete]")
    assert {m.value for m in Coupling} == {"tight", "moderate", "loose", "unknown"}
    print("  PASS")


def test_regime_enum_complete():
    print("[test_regime_enum_complete]")
    assert {m.value for m in Regime} == {
        "stationary", "drifting", "non_stationary", "unknown"
    }
    print("  PASS")


def test_scope_status_enum_complete():
    print("[test_scope_status_enum_complete]")
    assert {m.value for m in ScopeStatus} == {
        "in_scope", "edge_of_scope", "out_of_scope", "scope_undeclared",
    }
    print("  PASS")


def test_instrument_blind_spots_returns_list():
    print("[test_instrument_blind_spots_returns_list]")
    audit = _build_audit()
    bs = audit.instrument.blind_spots()
    assert isinstance(bs, list)
    assert len(bs) >= 4
    # noise floor and range must be surfaced explicitly
    assert any("noise floor" in s.lower() for s in bs)
    assert any("range" in s.lower() for s in bs)
    print(f"  {len(bs)} blind spots exposed")
    print("  PASS")


def test_protocol_filters_includes_excluded_conditions():
    print("[test_protocol_filters_includes_excluded_conditions]")
    audit = _build_audit()
    filters = audit.protocol.protocol_filters()
    assert "UV exposure" in filters
    assert "salt spray" in filters
    assert any("outlier" in f for f in filters)
    print(f"  {len(filters)} protocol filters declared")
    print("  PASS")


def test_coupling_summary_structure():
    print("[test_coupling_summary_structure]")
    audit = _build_audit()
    summary = audit.coupling.coupling_summary()
    assert set(summary.keys()) == {"instrument", "protocol", "substrate", "regime"}
    for v in summary.values():
        assert v in {"tight", "moderate", "loose", "unknown"}
    print(f"  coupling summary: {summary}")
    print("  PASS")


def test_regime_risk_categories():
    print("[test_regime_risk_categories]")
    # Each regime_state maps to a distinct risk string
    fixtures = [
        (Regime.STATIONARY, "LOW"),
        (Regime.DRIFTING, "MEDIUM"),
        (Regime.NON_STATIONARY, "HIGH"),
        (Regime.UNKNOWN, "UNKNOWN"),
    ]
    for state, prefix in fixtures:
        ra = RegimeAudit(
            assumed_baseline="test",
            baseline_validity_window="test",
            regime_state=state,
            regime_drift_indicators=[],
            extrapolation_horizon="test",
        )
        risk = ra.regime_risk()
        assert risk.startswith(prefix), f"{state.value}: expected {prefix}, got {risk!r}"
    print("  all 4 regime states produce distinct risk strings")
    print("  PASS")


def test_frame_fragility_categories():
    """Three risk levels for the causal-model audit; assert each
    is reachable."""
    print("[test_frame_fragility_categories]")
    base = dict(
        causal_frame="test",
        confounders_identified=[],
        confounders_controlled=[],
        alternative_frames_considered=[],
    )
    low = CausalModelAudit(
        **base, confounders_unmeasured=[], unknown_unknowns_acknowledged=True
    ).frame_fragility()
    medium = CausalModelAudit(
        **base, confounders_unmeasured=["a"], unknown_unknowns_acknowledged=True
    ).frame_fragility()
    high = CausalModelAudit(
        **base, confounders_unmeasured=["a"], unknown_unknowns_acknowledged=False
    ).frame_fragility()
    assert low.startswith("LOW")
    assert medium.startswith("MEDIUM")
    assert high.startswith("HIGH")
    # Per the code, unmeasured=0 + unknown_unknowns_acknowledged=False
    # falls into the HIGH branch -- confirms the fragility ladder
    edge = CausalModelAudit(
        **base, confounders_unmeasured=[], unknown_unknowns_acknowledged=False
    ).frame_fragility()
    assert edge.startswith("HIGH")
    print("  LOW/MEDIUM/HIGH all reachable")
    print("  PASS")


def test_scope_status_returns_enum():
    """scope_status_for must return a ScopeStatus, not a string.
    The placeholder _context_matches is naive (string-in-conditions)
    so we test with contexts crafted to land in each bucket."""
    print("[test_scope_status_returns_enum]")
    audit = _build_audit()

    # Context matching in_scope_conditions via key name
    in_scope = audit.scope.scope_status_for({"clean lab": True})
    assert in_scope == ScopeStatus.IN_SCOPE

    # Context matching out_of_scope_conditions
    out_scope = audit.scope.scope_status_for({"marine environment": True})
    assert out_scope == ScopeStatus.OUT_OF_SCOPE

    # Context matching edge_conditions
    edge = audit.scope.scope_status_for({"outdoor lab": True})
    assert edge == ScopeStatus.EDGE_OF_SCOPE

    # Context matching none -> undeclared
    undecl = audit.scope.scope_status_for({"totally unrelated thing": True})
    assert undecl == ScopeStatus.SCOPE_UNDECLARED
    print("  all 4 scope statuses reachable via naive matcher")
    print("  PASS")


def test_audit_report_shape_without_deployment():
    """Without deployment_context, report should carry the
    scope-undeclared warning verdict."""
    print("[test_audit_report_shape_without_deployment]")
    audit = _build_audit()
    report = audit.audit_report()
    required = {
        "claim", "instrument_blind_spots", "protocol_filters",
        "coupling_profile", "regime_risk", "causal_frame_fragility",
        "verdict",
    }
    assert required.issubset(report.keys()), f"missing: {required - set(report)}"
    assert "scope_status_for_deployment" not in report
    assert "scope-undeclared" in report["verdict"].lower() or "DO NOT" in report["verdict"]
    print("  shape correct; verdict warns against use without deployment context")
    print("  PASS")


def test_audit_report_shape_with_in_scope_deployment():
    print("[test_audit_report_shape_with_in_scope_deployment]")
    audit = _build_audit(deployment_context={"clean lab": True})
    report = audit.audit_report()
    assert report["scope_status_for_deployment"] == "in_scope"
    assert "valid within" in report["verdict"]
    # Even within scope, verdict refuses to call the claim a "law"
    assert "not a LAW" in report["verdict"]
    print(f"  verdict: {report['verdict'][:60]}...")
    print("  PASS")


def test_audit_report_out_of_scope_is_category_error():
    """The whole framework's point: out-of-scope deployment is a
    category error, not just a weak claim."""
    print("[test_audit_report_out_of_scope_is_category_error]")
    audit = _build_audit(deployment_context={"marine environment": True})
    report = audit.audit_report()
    assert report["scope_status_for_deployment"] == "out_of_scope"
    assert "category error" in report["verdict"]
    print("  verdict correctly names out-of-scope use as category error")
    print("  PASS")


def test_audit_report_edge_of_scope_requires_verification():
    print("[test_audit_report_edge_of_scope_requires_verification]")
    audit = _build_audit(deployment_context={"outdoor lab": True})
    report = audit.audit_report()
    assert report["scope_status_for_deployment"] == "edge_of_scope"
    assert "weakly supported" in report["verdict"]
    assert "independent verification" in report["verdict"]
    print("  PASS")


def test_historical_cases_structure():
    """The calibration corpus must carry the expected fields on
    each entry so downstream consumers can iterate them."""
    print("[test_historical_cases_structure]")
    assert len(HISTORICAL_CASES) >= 5
    for name, entry in HISTORICAL_CASES.items():
        assert "lesson" in entry, f"{name}: missing lesson"
        assert isinstance(entry["lesson"], str)
    print(f"  {len(HISTORICAL_CASES)} historical cases, all have lesson strings")
    print("  PASS")


def test_geocentrism_lesson_names_the_pattern():
    """The flagship case: geocentrism was scope-complete, not
    wrong. The lesson string must convey that."""
    print("[test_geocentrism_lesson_names_the_pattern]")
    geo = HISTORICAL_CASES["geocentrism"]
    lesson = geo["lesson"]
    assert "not 'wrong'" in lesson or "scope-complete" in lesson
    assert "Instrument expansion" in lesson or "instrument expansion" in lesson
    print("  PASS")


def test_prose_constants_are_nonempty():
    """PREMISE, AI_REASONING_RULE, META_INSIGHT are part of the
    public surface; consumers may read them directly."""
    print("[test_prose_constants_are_nonempty]")
    for name, s in [("PREMISE", PREMISE),
                    ("AI_REASONING_RULE", AI_REASONING_RULE),
                    ("META_INSIGHT", META_INSIGHT)]:
        assert isinstance(s, str)
        assert len(s.strip()) > 100, f"{name} suspiciously short"
    print("  all three prose constants non-empty and substantive")
    print("  PASS")


def test_reexported_via_package_root():
    """StudyScopeAudit must be reachable via `from logic_ferret
    import ...` (as the package is installed)."""
    print("[test_reexported_via_package_root]")
    import sys as _sys, importlib.util as _util, os as _os
    repo_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    spec = _util.spec_from_file_location(
        "logic_ferret",
        _os.path.join(repo_root, "__init__.py"),
        submodule_search_locations=[repo_root],
    )
    pkg = _util.module_from_spec(spec)
    _sys.modules["logic_ferret"] = pkg
    spec.loader.exec_module(pkg)
    # All study_scope_audit names must be present
    for name in ["Coupling", "Regime", "ScopeStatus", "StudyScopeAudit",
                 "InstrumentAudit", "ProtocolAudit", "PREMISE",
                 "AI_REASONING_RULE", "META_INSIGHT", "HISTORICAL_CASES"]:
        assert hasattr(pkg, name), f"{name} not re-exported via __init__.py"
    print("  all study_scope_audit names reachable via package root")
    print("  PASS")


if __name__ == "__main__":
    test_coupling_enum_complete()
    test_regime_enum_complete()
    test_scope_status_enum_complete()
    test_instrument_blind_spots_returns_list()
    test_protocol_filters_includes_excluded_conditions()
    test_coupling_summary_structure()
    test_regime_risk_categories()
    test_frame_fragility_categories()
    test_scope_status_returns_enum()
    test_audit_report_shape_without_deployment()
    test_audit_report_shape_with_in_scope_deployment()
    test_audit_report_out_of_scope_is_category_error()
    test_audit_report_edge_of_scope_requires_verification()
    test_historical_cases_structure()
    test_geocentrism_lesson_names_the_pattern()
    test_prose_constants_are_nonempty()
    test_reexported_via_package_root()
    print("\nall study_scope_audit tests passed.")
