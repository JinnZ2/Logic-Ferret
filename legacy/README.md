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

## Open questions

Things surfaced and **not** resolved. Written down so they are
searchable later rather than rediscovered. Resolved entries stay,
struck through with what closed them -- a question that vanishes on
being answered leaves no evidence it was ever open.

1. ~~**`README.md` describes a repo that no longer exists.**~~
   **RESOLVED.** Rewritten as an accurate front door: both entry
   points, the tier table, the nine layers, an explicit limits
   section, and an install path that works. `tests/test_packaging.py`
   now reads the README as a set of claims -- every `python <file>`
   command must name a file that exists, every relative link must
   resolve, and the phantom `requirements.txt` and
   `logic-ferret-gui/gui` paths are asserted absent.

2. ~~**`setup.py` still declares the GUI as the product.**~~
   **RESOLVED.** Renamed to `logic-ferret`; the version is now parsed
   out of `schema_contract.SCHEMA_VERSION` at build time instead of
   being a second hand-maintained literal, so the 0.1.0-vs-1.2.0 split
   cannot recur. `tests/` and `legacy/` are excluded from the
   distribution, `install_requires` is empty (the analysis core is
   pure stdlib), and a `pyproject.toml` was added so `pip install -e .`
   uses the PEP 517 path -- without it the legacy `setup.py develop`
   path fails on Debian and Ubuntu with
   `AttributeError: install_layout`.

3. **`fallacy_gui.py` was not retired.** It still runs and is a live
   `console_scripts` target, but it reaches exactly one of fourteen
   sensors (`annotate_text`). It is the original scope of the project,
   surviving as an entry point of the current one. Whether it should
   grow to the full suite or be retired to `legacy/` is a product
   decision, not a cleanup. It is now `logic-ferret-gui`, no longer
   the primary `logic-ferret` command.

4. **`truth_integrity_score.py` at repo root is a live shim**, not
   legacy -- it re-exports `calculate_c3` from the canonical module
   and works. Left in place. It has no test coverage.

5. **The `/ 10` normalizer in `logic_fallacy_ferret.assess()` has
   never been justified** in any version. Ten fallacies saturates the
   sensor; nine reads 0.9. Whether 10 is calibrated or arbitrary is
   unrecorded, and it survived the polarity fix unexamined.

6. ~~**`examples/offshore_wind_radar.txt` is referenced by nothing.**~~
   **RESOLVED.** The invocation is documented in `README.md`, and
   `tests/test_article_check.py` now runs the full pipeline against
   the file end to end, so it can no longer rot unnoticed.

7. **The repo declares two different licenses.** `LICENSE` at root is
   MIT (2025, JinnZ2). Every module in `knowledge/`, plus
   `knowledge/README.md`, declares `License: CC0` in its own
   docstring. These are not compatible statements about the same code.
   `setup.py` follows `LICENSE` because that is the conventional
   authority, and `tests/test_packaging.py` pins the two to agree --
   but the `knowledge/` docstrings are untouched, because changing a
   license claim is the owner's call and not a cleanup. If CC0 is
   intended for that subtree, it needs saying somewhere other than
   nine docstrings.

8. **The `practice/` question bank has never been tested on a
   reader.** The eight layer questions are derived from the pipeline's
   layers, which is principled, but "principled" is a hypothesis about
   pedagogy, not a result. Whether a person using the worksheet
   actually reads more carefully afterward is unmeasured. Recorded
   here rather than assumed, per the point of this directory.
