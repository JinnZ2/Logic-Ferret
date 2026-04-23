# CLAUDE.md

Navigation guide for AI assistants (and humans) working on
Logic-Ferret. Matches the convention in the sibling repos
(`metabolic-accounting`, `thermodynamic-accountability-framework`).

## What this repo is

Logic-Ferret detects rhetorical camouflage and discourse collapse
in text. The core is a sensor suite plus a 9-layer conflict-
diagnosis pipeline. A schema contract declares a stable public
surface that sibling frameworks (TAF, metabolic-accounting) can
mirror without runtime coupling.

## Module map

```
Logic-Ferret/
  schema_contract.py             # declared public surface; TAF mirrors this
  __init__.py                    # package root re-exports
  RELATED.md                     # sibling-framework network
  CLAUDE.md                      # this file

  sensor_suite/sensors/          # 14 text sensors, each with assess(text)
    conflict_diagnosis.py        # 9-layer pipeline; diagnose(); prints
    discourse_collapse.py        # Layer 9; only path to BLACK tier
    fallacy_overlay.py           # annotate_text()
    truth_integrity_score.py     # calculate_c3() composite
    propaganda_tone.py
    propaganda_bias.py
    gatekeeping_sensor.py
    false_urgency.py
    narrative_fragility.py
    agency_detector.py
    reward_manipulation.py
    gaslight_frequency_meter.py
    responsibility_deflection_sensor.py
    true_accountability_sensor.py
    meritocracy_detector.py
    logic_fallacy_ferret.py

  integrations/                  # adapters to sibling frameworks (standalone)
    financial_text.py            # v0 adapter for money_signal/investment_signal

  knowledge/                     # knowledge-liberation framework + reasoning companions
    README.md                    # operational pipeline docs
    scope_mapper.py              # operational: map a study's actual scope
    edge_explorer.py             # operational: 8 edge-of-scope questions
    application_builder.py       # operational: valid uses + misapplications
    knowledge_liberation.py      # operational: orchestrator
    interactive_navigator.py     # operational: non-linear graph navigation
    shadow_catalog.py            # operational: catalog of silence patterns
    recontextualizer.py          # operational: localize to user context
    study_scope_audit.py         # declarative companion: 6-layer scope audit
    informational_cost_audit.py  # motivational companion: cost of false certainty

  tests/                         # standalone scripts, no external runner
    run_all.py                   # convenience umbrella
    test_schema_contract.py
    test_layer9.py
    test_diagnose_integration.py
    test_c3.py
    test_ai_downstream.py
    test_longitudinal_drift.py
    test_financial_text.py
    test_study_scope_audit.py
    test_informational_cost_audit.py
```

## Intent routing

Use this to jump to the right module for what you're doing:

| You want to... | Start at |
|---|---|
| Check if a text shows camouflage | `sensor_suite.sensors.conflict_diagnosis.diagnose()` |
| Check if a text shows BLACK-tier collapse | `sensor_suite.sensors.discourse_collapse.detect()` |
| Run all sensors and get a composite score | `run_full_sensor_scan.py` |
| See what TAF can mirror | `schema_contract.ferret_surface()` |
| Pin signatures and fail on drift | `schema_contract.assert_signatures()` |
| Map a specific study's scope (operational) | `knowledge.scope_mapper.ScopeMapper` |
| Declare the 6-layer audit before citing a study | `knowledge.study_scope_audit.StudyScopeAudit` |
| Explain why false certainty is expensive | `knowledge.informational_cost_audit` (pure data) |
| Understand the tier taxonomy | `schema_contract.TIER_LEVELS` + `SIGNAL_TO_TIER` |
| See cross-framework integration | `RELATED.md` |

## Contracts and version promises

`schema_contract.SCHEMA_VERSION` uses semver:
- MAJOR: rename / remove / shape change (breaking)
- MINOR: new sensor or new flag key (additive)
- PATCH: docstring, typo, internal cleanup

Current version: see `schema_contract.SCHEMA_VERSION`
(as of the knowledge/ reconstruction work: 1.2.0).

The two companion modules in `knowledge/` (study_scope_audit,
informational_cost_audit) are **outside** the schema contract.
Their stability is documented via their `__all__` lists. They
are NOT versioned through `SCHEMA_VERSION`.

## Tests

`python tests/run_all.py` runs the whole suite via subprocess.
Each file is also directly executable:
`python tests/test_schema_contract.py` etc. No external runner,
no pytest dependency. 84 tests as of the last chunk before the
knowledge/ reconstruction.

## Known issues and reconstruction log

### Pre-existing damage in `knowledge/` operational pipeline

The seven operational files in `knowledge/` were committed to
main through a pipeline that mangled their Python structure.
Before reconstruction, all seven had `SyntaxError` on import and
could not be run standalone. The damage pattern was consistent:

1. Module-opening `"""docstring"""` turned into `# """` + orphan
   closing `"""` (the docstring opener became a Python comment;
   the closing delimiter became a stray string literal)
2. Markdown fenced-code-block markers (` ``` `) embedded inside
   docstrings
3. Smart/curly typography throughout (`"`, `"`, `'`, `'`, `—`)
   used as both delimiters and content
4. **All indentation stripped** from class bodies, function
   bodies, control-flow blocks -- everything flush-left

This was not caused by the schema-contract work (that work
landed in main in PR #6/#8 and did not touch `knowledge/`).
The damage arrived separately in commits `881c3f1`,
`76c4913`, `bf1758f`, `8dc9e97`, `c8b6a91`, `a1154e6`,
`c40247f`, `01b34c8` on main.

Reconstruction approach (see individual commits for per-file
detail):

- Preserve semantics verbatim; only fix what the mangler broke
- Restore Python indentation by inferring structure from
  `class` / `def` / `@decorator` / `if __name__` markers and
  docstring positions
- Remove Markdown fence artifacts (` ``` `) from inside
  docstrings
- Normalize smart characters to ASCII equivalents:
  `"`/`"` -> `"`, `'`/`'` -> `'`, `—` -> `--`, `–` -> `-`,
  `…` -> `...`, nbsp -> space, minus-sign -> hyphen
- Verify each file parses via `ast.parse` AND runs its
  `__main__` block (if it has one) without error before commit

Judgment-call flags (places where I had to choose between
plausible reconstructions) are noted per-file in the commit
messages. Any such spot is also marked in-source with a
`# RECONSTRUCTED: <note>` comment for later review.

| file | status | __main__ runs? |
|---|---|---|
| `knowledge/scope_mapper.py`          | RECONSTRUCTED | yes |
| `knowledge/edge_explorer.py`         | RECONSTRUCTED | yes |
| `knowledge/application_builder.py`   | RECONSTRUCTED | yes |
| `knowledge/knowledge_liberation.py`  | RECONSTRUCTED | yes |
| `knowledge/interactive_navigator.py` | pending | |
| `knowledge/shadow_catalog.py`        | pending | |
| `knowledge/recontextualizer.py`      | pending | |

(This table gets updated as each file is reconstructed.)

## Sibling frameworks

See `RELATED.md` for the cross-framework network. Short form:

- Logic-Ferret (this repo): rhetoric layer
- TAF (`thermodynamic-accountability-framework`): physics layer
- metabolic-accounting: accounting layer
- earth-systems-physics (planned): substrate layer

All publish stable schemas that peers mirror. No runtime
imports between frameworks; coupling is through declared
invariants only.
