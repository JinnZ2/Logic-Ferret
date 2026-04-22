# Related Frameworks

Logic-Ferret is one node in a small network of falsifiable
accountability frameworks. Each publishes a stable schema that
the others can "read alongside, not after" -- structural coupling
through declared invariants, not through code dependencies.

## The network

| Framework | Domain | Primary question |
|---|---|---|
| [Logic-Ferret](https://github.com/JinnZ2/Logic-Ferret) | Rhetoric | Is the narrative camouflage, or has the reasoning apparatus itself collapsed? |
| [Thermodynamic Accountability Framework (TAF)](https://github.com/JinnZ2/thermodynamic-accountability-framework) | Physics | Does the energy math close? Is exergy destruction accounted for? |
| [Metabolic Accounting](https://github.com/JinnZ2/metabolic-accounting) | Accounting | Are basins (soil, water, air, biology, community) on the balance sheet? Is regeneration debt tracked? |
| [Earth-Systems Physics](https://github.com/JinnZ2/earth-systems-physics) (planned) | Substrate | Does the money/investment signal couple to real planetary throughput? |

None of these frameworks imports from another at runtime.
Coupling is through structural invariants, declared surfaces,
and shared vocabulary. Run any two and the camouflage has fewer
places to hide. Run all four and the story has to survive
rhetoric, physics, accounting, and substrate simultaneously.

## Logic-Ferret's niche

Ferret is the rhetoric layer. It does not measure energy, dollars,
or soil carbon. It measures whether the words describing those
things are doing honest work.

Other frameworks can consume Ferret output when a stated reason
needs to be tested against physical, accounting, or substrate
reality. Ferret can consume other frameworks' output when
someone is writing text about a claim -- a prospectus, a policy
memo, an annual report -- and we want to check whether the
rhetoric about the numbers matches what the numbers actually say.

## Shared vocabulary

Three cross-framework conventions Logic-Ferret participates in:

**GREEN / AMBER / RED / BLACK tier taxonomy.** Same four-level
severity encoding as `metabolic-accounting/distributional/tiers.py`
and TAF's verdict layer. Logic-Ferret v1.1.0 adopted the vocabulary
directly; see `schema_contract.TIER_LEVELS`. BLACK means "past
the level where the system's own corrective mechanisms can
recover" -- thermodynamically irreversible in TAF and
metabolic-accounting, discourse-collapsed (Layer 9) in Ferret.

**Tier vector preservation.** Per metabolic-accounting invariant
#6: "code that calls `overall_tier()` and discards the vector"
caused a documented bug. Ferret exposes per-layer and per-sensor
tier vectors (`layer_tiers()`, `sensor_tiers()`) so consumers
can see *which* signal is hot, not just the composite.

**Schema contract with declared surface.** A single
`schema_contract.py` at the package root declares version,
sensor names, layer names, tier vocabulary, and function
signatures. `ferret_surface()` returns a JSON-serializable
snapshot. `assert_signatures()` lets consumers pin and fail
loud on drift.

## Integration sketches (not yet implemented)

### TAF <-> Ferret  (handshake is live and two-way)

Confirmed present on TAF's side:

- `thermodynamic-accountability-framework/schemas/logic_ferret_contract.py`
  -- declared mirror of this contract. Pins `UPSTREAM_SCHEMA_VERSION`
  and re-declares sensor names, layer names, signal levels, and
  `LayerResult` / `DiagnoseResult` shapes so TAF can validate our
  surface at startup via `validate_ferret_surface()`.
- `thermodynamic-accountability-framework/core/integrations/ferret_fieldlink.py`
  -- runtime bridge. Uses the contract mirror to route Ferret
  outputs into TAF's accounting.

Same pattern applied to every TAF sibling:
`schemas/metabolic_accounting_contract.py`,
`schemas/mathematic_economics_contract.py`,
`schemas/trust_exit_contract.py`.

**Version lag to note:** TAF's logic_ferret_contract.py was last
pinned at our v1.0.0. Everything from v1.1.0 forward (tier
taxonomy, Layer 9 discourse_collapse, BLACK tier, `tier` +
`discourse_collapse` fields on `DiagnoseResult`, Discourse
Collapse sensor) is additive and backward-compatible -- TAF's
v1.0 pin still validates against our current surface, they just
can't *see* the new fields until they refresh. If TAF adopts
`assert_signatures` to pin signature strings (not just the
surface snapshot), they'll get a clean `SignatureMismatch` on
our `diagnose()` signature drift and know exactly what to update.

Two purposes the bridge serves: (1) route specific Ferret sensor
scores into TAF's social-overhead accounting, and (2) elevate
TAF's irreversibility flags into BLACK when paired with Ferret's
discourse-collapse signals on the same text.

Cross-reference map:

| TAF module | Logic-Ferret signal |
|---|---|
| Narrative Stripper | Stated Problem + Feasibility Gap (Layers 1-2) |
| Social Overhead Accountant | Systemic Alignment (Layer 4) |
| Root Cause Depth Analyzer | Hidden Driver + Consequence (Layers 5-6) |
| Friction Ratio | Camouflage Score |
| Energy Conservation | Consequence divergence |
| Entropy growth | Feedback Loops (Layer 8) |
| Irreversibility (past-cliff) | Discourse Collapse (Layer 9) -> BLACK |

### Metabolic-Accounting <-> Ferret

Metabolic-accounting publishes stable types (`BasinState`,
`GlucoseFlow`, `Verdict`, tier assignments) via `docs/SCHEMAS.md`.
Ferret can consume these when analyzing text *about* regeneration
debt, basin depletion, or infrastructure cascade -- verifying
whether the rhetoric about the numbers matches what the numbers
say.

Money-signal and investment-signal modules (new in
metabolic-accounting as of 2026) publish coupling matrices for
trust-collapse and substrate-vector analysis. These are
candidates for Ferret consumption when parsing prospectuses,
10-Ks, or policy statements about financial claims.

## Companion modules in `knowledge/`

Two reasoning-discipline modules live alongside the
knowledge-liberation framework in `knowledge/`. Neither is a
text sensor; neither lives in `SENSOR_REGISTRY` or on
`ferret_surface()`. They share the folder because they share
the same epistemic stance: treat confident claims as
scope-bounded measurements, not as laws.

They join an existing operational pipeline in `knowledge/`
(`scope_mapper.py`, `edge_explorer.py`, `application_builder.py`,
`knowledge_liberation.py` orchestrator, plus `interactive_navigator.py`,
`shadow_catalog.py`, `recontextualizer.py` -- see
`knowledge/README.md`). The two companions are the declarative
and motivational sides of the same discipline:

- `knowledge/study_scope_audit.py` -- the *structural* side. Six-layer
  audit (instrument, protocol, coupling, regime, causal model,
  scope boundary) that a reasoning agent must declare BEFORE
  citing a study as evidence. Scope-bounded verdicts
  (IN/EDGE/OUT/UNDECLARED) replace true/false.

- `knowledge/informational_cost_audit.py` -- the *accounting* side. Why
  false certainty is expensive informationally: each anomaly
  adds an epicycle, each epicycle is committed debt, regime
  shift collapses the whole stack. Uncertainty appears costly
  upfront but pays linearly; certainty appears cheap but
  accumulates exponentially. The geocentric-to-heliocentric
  case worked through as data (HISTORICAL_PATTERN,
  INFORMATION_COST_AUDIT, AI_IMPLICATIONS, VERDICT).

Read alongside the operational pipeline: `scope_mapper` produces
a structured map of what a specific study actually measured;
`study_scope_audit` declares the layers that must be audited
before the claim is cited anywhere; `informational_cost_audit`
explains why deferring that audit is ruinous.

Two readings of the same discipline, useful in combination:
study_scope_audit tells you *how* to declare scope; the cost
audit tells you *why* the alternative (deferring scope
declaration) is ruinous. A reasoning agent uses the first to
produce honest citations and the second to resist the
comfort-pull that erodes them.

Both are **outside the schema contract** -- the text-analysis
surface stays scoped to text. Both re-export through
`__init__.py`. The `VERDICT` dict from informational_cost_audit
is aliased to `INFORMATIONAL_COST_VERDICT` at package scope to
keep a generic name from colliding with future additions.

### study_scope_audit usage

```python
from knowledge.study_scope_audit import StudyScopeAudit  # or from logic_ferret
audit = StudyScopeAudit(
    claim=..., citation=...,
    instrument=InstrumentAudit(...),
    protocol=ProtocolAudit(...),
    coupling=DomainCouplingAudit(...),
    regime=RegimeAudit(...),
    causal_model=CausalModelAudit(...),
    scope=ScopeBoundary(...),
    deployment_context={"marine environment": True},
)
audit.audit_report()  # returns scope-bounded verdict + blind spots
```

Historical calibration corpus in `HISTORICAL_CASES` covers
geocentrism, miasma theory, caloric theory, steady-state
cosmology, and low-fat-diet consensus -- each showing the same
pattern: *correct within instrument scope, revealed as incomplete
when the measurable domain expanded*.

### informational_cost_audit usage

```python
from knowledge.informational_cost_audit import (
    INFORMATION_COST_AUDIT, VERDICT, AI_IMPLICATIONS,
)

# Side-by-side cost comparison of commitment vs. uncertainty
INFORMATION_COST_AUDIT["geocentrism_path"]["cost_when_regime_shifts"]
# -> "CATASTROPHIC -- everything has to be rebuilt from scratch..."

VERDICT["one_liner"]
# -> "false certainty is a loan that comes due when the
#     measurement frontier advances. honest uncertainty pays
#     as you go."

AI_IMPLICATIONS["the_real_question_for_AI"]
# -> "are you optimizing for apparent low cost NOW, or for
#     true low cost OVER TIME? comfort vs. resilience?"
```

Pure-data module -- dicts and lists, no functions. Intended to
be read directly by AI systems as part of their reasoning
prelude, the way a system prompt is. `HISTORICAL_PATTERN`
enumerates the nine-step recurrence that the scope audit exists
to interrupt.

## Versioning promise

Each framework publishes a `SCHEMA_VERSION`. Cross-framework
consumers pin both ends. A minor bump is additive; a major bump
is a breaking change. Drift is detected at startup via each
framework's equivalent of `assert_signatures()`.

---

Logic-Ferret schema version: see `schema_contract.SCHEMA_VERSION`.
