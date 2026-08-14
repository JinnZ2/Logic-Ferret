# Logic-Ferret

**Spot the nonsense. Smack the source.**

Detects rhetorical camouflage and discourse collapse in text -- the gap
between what a piece of writing says it is about and what it is doing.

Pure standard library. No dependencies, no network, no model calls. It
runs offline on a laptop from 2011.

---

## Two ways in

The repo has a machine half and a human half, and they are meant to be
used against each other.

| | |
|---|---|
| **You want the sensors to read a text** | `run_conflict_diagnosis.py` |
| **You want to practice reading it yourself** | `run_article_check.py` |

### Machine: diagnose a text

```bash
python run_conflict_diagnosis.py examples/offshore_wind_radar.txt
```

Runs the 9-layer pipeline and prints a diagnostic table plus a
flowchart trace. Add `--json` for downstream tools, `--table` or
`--flow` for one or the other.

Every sensor at once, with a composite score:

```bash
python run_full_sensor_scan.py examples/offshore_wind_radar.txt
```

### Human: check your own reading

```bash
python run_article_check.py --worksheet > sheet.txt   # print it, fill it in
python run_article_check.py article.txt               # then enter your read
```

A structured critical-thinking check you run on an article. Eight
questions, one per diagnosis layer, plus five open ones -- including
the only question on the sheet that really matters:

> What specific evidence would change your mind?

**You answer first, blind. Then the ferret answers. Then you compare.**
The tool will not show you a score until you have committed to a read,
because a number shown first stops being evidence and starts being an
anchor.

Divergence is the output. Where you rated a layer higher than the
sensors did, you probably saw structure they cannot see. Where they
rated higher, go read the phrases they matched. Where you agreed, that
is weak evidence and the report says so. There is no grade -- matching
a keyword matcher perfectly would mean you had become one.

See [`practice/README.md`](practice/README.md).

---

## What is in here

```
schema_contract.py    Declared public surface. Sibling frameworks mirror this.
sensor_suite/         14 text sensors, each with assess(text) -> (score, flags)
practice/             The human-facing check
knowledge/            Scope-mapping toolkit: what a study actually measured
integrations/         Adapters to sibling frameworks
legacy/               Superseded files, kept not deleted, with a lineage record
tests/                140 tests, no external runner
```

### The tiers

Every score lands in one of four tiers, used identically by the
sensors and by the human check so the two are directly comparable:

| Tier | Meaning |
|---|---|
| `GREEN` | Clear. |
| `AMBER` | Vague, partial, unexamined. |
| `RED` | Actively misleading. |
| `BLACK` | Not an argument -- reasoning itself is under attack. |

`BLACK` is reachable only through Layer 9, discourse collapse. No
amount of ordinary camouflage adds up to it.

### The nine layers

Layers 1-8 look for camouflage: `Stated Problem`, `Feasibility Gap`,
`Incentive Mapping`, `Systemic Alignment`, `Consequence Analysis`,
`Hidden Driver`, `Peripheral Signals`, `Feedback Loops`. Layer 9 looks
for collapse.

---

## Honest limits

The sensors match keywords and patterns. They have no idea what a text
is about.

Run the article check on the shipped example and you can watch them
over-fire: `Peripheral Signals` goes RED on "Engineers say" and
"Veterans say" -- ordinary attribution verbs -- and `Systemic
Alignment` goes RED on "budget" and "spending". A high score means
"this text uses flagged vocabulary densely", which is *evidence about*
camouflage, not a verdict on it. A real emergency contains urgency
words.

This is why the human half exists, and why the comparison runs in that
order.

---

## As a library

```python
from sensor_suite.sensors.conflict_diagnosis import diagnose

result = diagnose(text)
result["tier"]              # GREEN | AMBER | RED | BLACK
result["camouflage_score"]  # 0.0 - 1.0
result["layers"]            # per-layer signal + matched evidence
```

The stable surface is declared in `schema_contract.py` and versioned
with semver (`SCHEMA_VERSION`). Sibling frameworks mirror the contract
rather than importing this package -- there are no runtime imports
between frameworks. A consumer keeps its own pinned copy of the
signatures and hands it back on import:

```python
from schema_contract import assert_signatures
assert_signatures(MY_PINNED_SIGNATURES)   # raises SignatureMismatch on drift
```

## Install

```bash
git clone https://github.com/JinnZ2/Logic-Ferret
cd Logic-Ferret
python tests/run_all.py      # optional: confirm it works
```

Nothing to install. `pip install -e .` also works and adds the
`logic-ferret` and `logic-ferret-check` commands.

There is a Tkinter GUI (`python fallacy_gui.py`) but it reaches only
one of the fourteen sensors. It is the original scope of the project,
kept working; the CLIs above are the current one.

## Contributing

Superseded files get retired to `legacy/` with a lineage entry, never
deleted -- deleting a falsified file deletes the falsification with it.
The convention and the reasoning are in
[`CLAUDE.md`](CLAUDE.md#retiring-a-file-the-legacy-convention), and
[`legacy/README.md`](legacy/README.md) is the running record of what
changed and why.

## Sibling frameworks

[Thermodynamic Accountability Framework (TAF)](https://github.com/JinnZ2/thermodynamic-accountability-framework)
measures institutional failure through physics. Logic-Ferret measures
it through rhetoric. TAF asks "does the energy math close?" while the
Ferret asks "is the narrative camouflage?" Run both and the bullshit
has nowhere left to hide.

| TAF Module | Logic Ferret Sensor | Shared Diagnostic |
|---|---|---|
| Narrative Stripper | Stated Problem + Feasibility Gap | Strip the story, check if it holds |
| Social Overhead Accountant | Systemic Alignment | Performance theater vs. actual outcomes |
| Root Cause Depth Analyzer | Hidden Driver + Consequences | Trace past symptoms to structure |
| Friction Ratio | Camouflage Score | Single number: how much is waste/cover? |
| Energy Conservation | Consequence divergence | Promised output vs. actual output |
| Entropy growth | Feedback Loops | Self-reinforcing decay the system won't fix |

Full network in [`RELATED.md`](RELATED.md).

## License

MIT -- see [`LICENSE`](LICENSE).

---

*A feral member of the Logic Monk Stack. Built for the tired minds who
still believe truth matters.*
