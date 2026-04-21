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

## Companion module: `study_scope_audit`

`study_scope_audit.py` at the repo root is a **separate public
API** alongside the schema contract. It is not a text sensor; it
does not participate in `SENSOR_REGISTRY` or `ferret_surface()`.
It lives here because its purpose complements Ferret's core job:
where Ferret catches rhetoric that obscures a claim, the
scope-audit catches reasoning that cites a claim beyond the
scope it was measured in.

Use case: an AI reasoning agent about to cite a study as
evidence. The audit forces seven-layer declaration -- instrument
blind spots, protocol filters, coupling strength, regime
stability, causal-model fragility, scope boundary, and
deployment-context match -- before the citation is allowed to
land as evidence rather than analogy.

```python
from study_scope_audit import StudyScopeAudit  # or from logic_ferret
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

Why this lives with Ferret and not in a sibling repo: both modules
share one epistemic stance -- treat confident claims as
scope-bounded measurements, not as laws. Ferret enforces this on
the rhetoric side; `study_scope_audit` enforces it on the
citation side. Same discipline, different surface area.

Outside the schema contract. Consumers import directly; it is
not versioned via `SCHEMA_VERSION`. Its stability comes from its
public dataclass surface, which is documented via `__all__`.

## Versioning promise

Each framework publishes a `SCHEMA_VERSION`. Cross-framework
consumers pin both ends. A minor bump is additive; a major bump
is a breaking change. Drift is detected at startup via each
framework's equivalent of `assert_signatures()`.

---

Logic-Ferret schema version: see `schema_contract.SCHEMA_VERSION`.
