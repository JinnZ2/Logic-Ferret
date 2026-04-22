# knowledge/__init__.py
#
# The knowledge-liberation framework. Most modules in this folder
# are operational tools (scope_mapper, edge_explorer, application_builder,
# knowledge_liberation, interactive_navigator, shadow_catalog, recontextualizer).
# They use absolute imports of each other (e.g. `from scope_mapper import ...`)
# and are designed to be run standalone from this directory or with this
# directory on sys.path. Those existing modules are NOT re-exported here --
# doing so would trigger their absolute-import resolution in a package
# context, which is not supported by their authoring convention.
#
# This __init__.py exposes the two declarative/motivational companions
# that join this folder from the epistemology side:
#
#   study_scope_audit       -- six-layer audit for scope-bounded citation
#   informational_cost_audit -- why false certainty accumulates epicycle debt
#
# Both are self-contained (no cross-imports within knowledge/) and safe
# to expose through the package __init__.

from .study_scope_audit import (
    Coupling,
    Regime,
    ScopeStatus,
    InstrumentAudit,
    ProtocolAudit,
    DomainCouplingAudit,
    RegimeAudit,
    CausalModelAudit,
    ScopeBoundary,
    StudyScopeAudit,
    PREMISE,
    AI_REASONING_RULE,
    META_INSIGHT,
    HISTORICAL_CASES,
)

from .informational_cost_audit import (
    GEOCENTRIC_COMFORT_STATE,
    ANOMALIES_UNDER_GEOCENTRISM,
    INFORMATION_COST_ACCUMULATION,
    HELIOCENTRIC_UNCERTAINTY_STATE,
    INFORMATION_COST_AUDIT,
    INFORMATION_THEORY_INSIGHT,
    AI_IMPLICATIONS,
    HISTORICAL_PATTERN,
    VERDICT,
)

__all__ = [
    # study_scope_audit
    "Coupling", "Regime", "ScopeStatus",
    "InstrumentAudit", "ProtocolAudit", "DomainCouplingAudit",
    "RegimeAudit", "CausalModelAudit", "ScopeBoundary",
    "StudyScopeAudit",
    "PREMISE", "AI_REASONING_RULE", "META_INSIGHT", "HISTORICAL_CASES",
    # informational_cost_audit
    "GEOCENTRIC_COMFORT_STATE", "ANOMALIES_UNDER_GEOCENTRISM",
    "INFORMATION_COST_ACCUMULATION", "HELIOCENTRIC_UNCERTAINTY_STATE",
    "INFORMATION_COST_AUDIT", "INFORMATION_THEORY_INSIGHT",
    "AI_IMPLICATIONS", "HISTORICAL_PATTERN", "VERDICT",
]
