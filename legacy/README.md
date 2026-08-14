# legacy/

Superseded files. **Kept, not deleted** -- their precedence still
carries. Each one is the ancestor of something live, and in two of
three cases the ancestor is the only surviving record of a claim that
got tested and edited.

Nothing here is imported by live code. Nothing here is packaged
(there is deliberately no `__init__.py`, so `find_packages()` skips
this directory). `tests/test_legacy_quarantine.py` enforces both.

## Why keep it

The repo is built by the loop it also measures for: hypothesize, run,
read the result, edit the claim, look for what you didn't ask, rerun.
Deleting a falsified file deletes the falsification with it. What
remains is a codebase that looks like it was right the first time --
which is exactly the "comfort is expensive" failure that
`knowledge/informational_cost_audit.py` is about. A repo that hides
its own edits is making the geocentric bet.

So the rule here is: when a claim gets edited, the superseded file
moves to `legacy/` and gets an entry below recording what was
claimed, what falsified it, and what the claim became.

## Recovering lineage

Git already knows the descent. These files were not copied and
re-created -- their descendants were forked from them in place, so
`--follow` walks straight through:

```
git log --follow -- sensor_suite/sensors/logic_fallacy_ferret.py
git log --follow -- legacy/Logic_fallacy_ferret.py
```

Both bottom out at the same 2025-07-24 commit.

---

## `Logic_fallacy_ferret.py` -- FALSIFIED (polarity)

| | |
|---|---|
| Born | `e4f377b`, 2025-07-24, at repo root |
| Superseded by | `sensor_suite/sensors/logic_fallacy_ferret.py` |
| Superseding commit | `1e27a21`, 2026-04-07 |

**Claim.** A fallacy score should read as cleanliness -- more
fallacies, lower score:

```python
score = 1.0 - min(total / 10, 1.0)  # crude inverse score
```

**Result: falsified.** Every other sensor in the suite emits
*higher = more signal detected*. `calculate_c3()` sums weighted
sensor scores without per-sensor polarity handling, so an inverted
sensor does not merely read backwards -- it cancels the sensors that
agree with each other, and the composite silently understates
distortion on exactly the texts the suite exists to catch.

`1e27a21` found the same bug in `gaslight_frequency_meter.py` and
recorded it in the commit message: *"flipped polarity so higher score
= more gaslighting detected (was inverted vs all other sensors,
corrupting C3 composite)."*

**Edited claim.** Polarity is a suite-wide invariant, not a
per-sensor choice:

```python
score = min(total / 10, 1.0)  # higher = more fallacies detected
```

**What still carries.** The detection body is unchanged --
`annotate_text()`, sum the counts, divide by 10, clamp at 1.0. Only
the sign was wrong. The `/ 10` normalizer was never justified in
either version and is still unexamined (see Open questions).

**Note.** This file does not run. It was stranded at repo root with
`from .fallacy_overlay import ...`, and there is no `fallacy_overlay`
at root -- so it raises `ImportError` on import. It was dead from the
day the corrected copy landed, which is why the inverted polarity
survived a year without being noticed. That is the useful part of the
record: *a falsified claim in an unreachable file does not announce
itself.*

---

## `propaganda_tone.py` -- SUPERSEDED (orphaned duplicate)

| | |
|---|---|
| Born | `2e0f2cd`, 2025-07-24, at `sensor_suite/propaganda_tone.py` |
| Superseded by | `sensor_suite/sensors/propaganda_tone.py` |
| Superseding commit | `1e27a21`, 2026-04-07 |

**No falsification.** Byte-identical to the live module. `1e27a21`
copied it one level down into `sensors/` "where imports expect it"
and left the original in place. Every importer resolves
`sensor_suite.sensors.propaganda_tone`; nothing has referenced this
path since.

Kept only so the duplicate is visibly retired rather than quietly
deleted -- and as the reason the quarantine test exists. Two
importable copies of one sensor is a live hazard: edit the wrong one
and the fix does nothing.

---

## `weights.txt` -- HYPOTHESIS, LARGELY CONFIRMED

| | |
|---|---|
| Born | `fe1755d`, 2025-07-24 |
| Implemented in | `sensor_suite/sensors/truth_integrity_score.py` |
| Extended by | `1ed7ae2`, 2026-04-21 |

This is a design note, never loaded by code. It is the *original
weighting hypothesis* for the composite Truth Integrity Score:

> Not all distortion is equal. [...] we assign weights based on how
> much the distortion disrupts clarity and choice.

**Result: 7 of 7 weights survived contact with the implementation,
unchanged.**

| `weights.txt` | `_WEIGHTS` | weight |
|---|---|---|
| Propaganda Tone | Propaganda Tone | 1.2 |
| Reward Manipulation | Reward Manipulation | 1.0 |
| False Urgency | False Urgency | 1.1 |
| Gatekeeping | Gatekeeping | 1.3 |
| Narrative Fragility | Narrative Fragility | 1.4 |
| Propaganda Bias Index | Propaganda Bias | 1.5 |
| Agency Restriction | Agency Score | 1.6 |
| -- | **Discourse Collapse** | **2.0** |

Only the two sensor *names* were edited to match the keys the sensors
actually emit. The ordering hypothesis -- that agency restriction
outranks bias outranks fragility, down to reward manipulation as the
floor -- is intact.

**Edited claim (one addition).** `1ed7ae2` added Discourse Collapse
at 2.0, above the entire original scale, because it is the only
sensor whose full-score emission means BLACK tier: collapse of the
reasoning apparatus itself, not camouflage over intact reasoning. The
original note had no concept of a tier above "existential threat to
autonomy," so this is a genuine extension, not a correction.

**Second-order result, recorded in the live source.** Adding a 2.0
weight exposed something the note never anticipated: because C3
normalizes by `weight_sum`, a lone BLACK discourse signal with every
other sensor quiet still reads ~0.12. The claim was edited to scope
C3 rather than to change the arithmetic -- *C3 is a composite
integrity signal, not a tier readout; for routing, read
`diagnose()["tier"]` directly.* See the comment block in
`truth_integrity_score.py`.

**What still carries.** The philosophy paragraph is the only written
justification for why these numbers and not others. The live module
documents Discourse Collapse's 2.0 and the dilution behavior, but
inherits 1.0-1.6 without restating the reasoning. Delete this file
and the rationale for seven of eight weights goes with it.

---

## Open questions (unrun)

Things this pass surfaced and did **not** resolve. Written down so
they are searchable later rather than rediscovered.

1. **`README.md` describes a repo that no longer exists.** It
   presents Logic-Ferret as a Tkinter GUI. Its quick start is
   `pip install -r requirements.txt` (no such file) and
   `cd logic-ferret-gui/gui` (no such directory). It does not mention
   the sensor suite, the 9-layer pipeline, `schema_contract`, or
   `knowledge/`. Not moved here: it is the repo's front door, and
   replacing it is a scope call for the owner.

2. **`setup.py` still declares the GUI as the product** --
   `name="logic-ferret-gui"`, version `0.1.0`, description "A
   sarcastic bullshit detector GUI", `install_requires=["tk"]`,
   entry point `fallacy_gui:main`. Meanwhile `schema_contract.py`
   independently versions the public surface at `1.2.0`. Two version
   numbers, neither referencing the other. Changing a published
   package name is outward-facing, so it was left alone.

3. **`fallacy_gui.py` was not retired.** It still runs and is the
   live `console_scripts` target, but it reaches exactly one of
   fourteen sensors (`annotate_text`). It is the original scope of
   the project, surviving as the entry point of the current one.
   Whether it should grow to the full suite or be retired to
   `legacy/` is a product decision, not a cleanup.

4. **`truth_integrity_score.py` at repo root is a live shim**, not
   legacy -- it re-exports `calculate_c3` from the canonical module
   and works. Left in place. It has no test coverage.

5. **The `/ 10` normalizer in `logic_fallacy_ferret.assess()` has
   never been justified** in any version. Ten fallacies saturates the
   sensor; nine reads 0.9. Whether 10 is calibrated or arbitrary is
   unrecorded, and it survived the polarity fix unexamined.

6. **`examples/offshore_wind_radar.txt` is undocumented, not
   unusable.** No test, README, or runner names it. It does work --
   both runners accept it and the pipeline scores it RED:

   ```
   python run_full_sensor_scan.py examples/offshore_wind_radar.txt
   python run_conflict_diagnosis.py examples/offshore_wind_radar.txt
   ```

   Recording the invocation here because it took reading two runners
   to recover it, and nothing else in the repo says it.
