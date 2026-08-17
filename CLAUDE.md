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

  practice/                      # human-facing exercises (outside the contract)
    README.md                    # how the article check works and why
    article_check.py             # question bank + blind-first comparison
  run_article_check.py           # CLI: worksheet, interactive, --answers replay

  integrations/                  # adapters to sibling frameworks (standalone)
    financial_text.py            # v0 adapter for money_signal/investment_signal

  legacy/                        # superseded files, kept not deleted
    README.md                    # lineage record: claim -> result -> edit
    Logic_fallacy_ferret.py      # FALSIFIED: inverted score polarity
    propaganda_tone.py           # SUPERSEDED: orphaned duplicate
    weights.txt                  # HYPOTHESIS: 7 of 8 C3 weights, confirmed

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
    test_knowledge_integrity.py  # damage-pattern regression guard + smoke tests
    test_legacy_quarantine.py    # legacy/ inertness + lineage record
    test_article_check.py        # question bank, comparison, blind-first order
    test_packaging.py            # setup.py/README claims checked as claims
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
| Match a study against known silence patterns | `knowledge.shadow_catalog.ShadowCatalog.diagnose()` |
| Localize a silence to your own context | `knowledge.recontextualizer.Recontextualizer` |
| Declare the 6-layer audit before citing a study | `knowledge.study_scope_audit.StudyScopeAudit` |
| Explain why false certainty is expensive | `knowledge.informational_cost_audit` (pure data) |
| Understand the tier taxonomy | `schema_contract.TIER_LEVELS` + `SIGNAL_TO_TIER` |
| See cross-framework integration | `RELATED.md` |
| Practice reading an article yourself | `run_article_check.py` |
| Print a no-computer worksheet | `run_article_check.py --worksheet` |
| Find out why a claim changed | `legacy/README.md` |
| Retire a superseded file | `legacy/` + an entry (see below) |

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

`practice/` is outside the contract for the same reason: it is
pedagogy, and it should be free to change without a version bump.
Its stability is documented by `__all__` in `practice/__init__.py`.

`setup.py` no longer carries its own version literal -- it parses
`SCHEMA_VERSION` out of `schema_contract.py` at build time. Two
hand-maintained version numbers is how the package spent a year
claiming 0.1.0 while the contract said 1.2.0.

## The blind-first rule in practice/

`practice/article_check.py` must not reveal machine output before a
complete human read exists. `machine_read()` is called only after
`HumanRead.validate()` passes, and the blank worksheet renders without
importing the sensor suite at all.

This is not stylistic. Showing a reader a camouflage score and then
asking what they think produces agreement, not judgment -- and it
would still look like the tool was working. Two tests pin it:
`test_machine_read_not_reachable_from_worksheet` and
`test_report_requires_complete_read`. An unrated layer raises rather
than defaulting to GREEN, because defaulting would credit the reader
with a judgment they never made.

The report deliberately refuses to grade.
`test_agreement_is_not_reported_as_success` asserts that the phrases
"not a grade" and "weak evidence" appear, and that congratulatory
framing does not.

## Retiring a file (the legacy/ convention)

This repo advances by the loop it also measures for: hypothesize,
run, read the result, edit the claim, look for what you didn't ask,
rerun. **Deleting a falsified file deletes the falsification with
it** -- what's left looks like it was right the first time, which is
the exact failure `knowledge/informational_cost_audit.py` is about.

So superseded files are retired, not deleted:

1. `git mv` the file into `legacy/` (never copy -- `git log --follow`
   must keep walking through to the ancestor).
2. Add an entry to `legacy/README.md` under a heading of the form
   `## <filename> -- VERDICT` (filename in backticks), recording the
   original claim, what falsified it (or that nothing did), the
   edited claim, and what still carries forward.
3. Add a `Superseded by` row to that entry's table, pointing at the
   live path, so the lineage pointer resolves.
4. If the edit fixed a real defect, pin it with a regression test so
   the falsified form cannot silently return.

`legacy/` deliberately has **no `__init__.py`** -- it must stay
un-importable and unpackaged. `tests/test_legacy_quarantine.py`
enforces every point above: quarantine inertness, documentation
completeness, pointer resolution, and the two current regression pins
(sensor polarity, C3 weight table).

Anything found but not resolved goes in that README's **Open
questions** section rather than into a commit message, where it
stops being searchable.

## Tests

`python tests/run_all.py` runs the whole suite via subprocess.
Each file is also directly executable:
`python tests/test_schema_contract.py` etc. No external runner,
no pytest dependency. 141 tests across 13 files as of the
completion of the knowledge/ reconstruction, the legacy/
quarantine, and the practice/ article check.

`tests/test_knowledge_integrity.py` is the regression guard for
the damage described below. It asserts each of the four damage
signatures against every file in `knowledge/`, runs every
`__main__` demo block, and smoke-tests the behavior of
`shadow_catalog` and `recontextualizer`. If the mangling pipeline
runs again, this file fails with a message naming the signature
rather than a bare `SyntaxError`.

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
| `knowledge/interactive_navigator.py` | RECONSTRUCTED | yes |
| `knowledge/shadow_catalog.py`        | RECONSTRUCTED | yes |
| `knowledge/recontextualizer.py`      | RECONSTRUCTED | yes |

**Reconstruction complete.** All seven operational modules parse,
import, and run their demo blocks. `tests/test_knowledge_integrity.py`
holds the line.

Judgment calls in the final two files:

- `shadow_catalog.py` -- none. Every fenced block sat at exactly one
  indent level inside a `class` or `def`, so structure was
  unambiguous. The 12 seeded patterns are pinned by ID in the test.
- `recontextualizer.py` -- one. The continuation line of
  `recontextualize_silences(silences, context)` arrived flush-left;
  it was realigned under the open paren. Noted in-source.

Both files were rebuilt by a scripted transform that applied only
whitespace and delimiter repairs, then verified that the multiset of
non-whitespace tokens was unchanged except for the removed fence
markers and the `**name**`/`**main**` -> `__name__`/`__main__`
repair. That check is what rules out silent content drift during
re-indentation.

## Sibling frameworks

See `RELATED.md` for the cross-framework network. Short form:

- Logic-Ferret (this repo): rhetoric layer
- TAF (`thermodynamic-accountability-framework`): physics layer
- metabolic-accounting: accounting layer
- earth-systems-physics (planned): substrate layer

All publish stable schemas that peers mirror. No runtime
imports between frameworks; coupling is through declared
invariants only.
