# practice/

Human-facing exercises. The rest of this repo points sensors at text;
this points questions at a person.

License: CC0

## The article check

A structured read you do on an article, compared afterward against
what the sensor suite found.

```
python run_article_check.py --worksheet > sheet.txt   # print it
python run_article_check.py article.txt               # then enter your read
```

**You answer first, blind. Then the ferret answers. Then you compare.**

That order is the whole design. If the tool showed you a camouflage
score first, you would read the article looking for what the number
told you to find, and it would feel like insight. So `machine_read()`
is not called until a complete `HumanRead` exists -- the runner cannot
show you a score early even if you want it to.

### What you answer

Eight questions, one per diagnosis layer, each rated GREEN / AMBER /
RED on the same scale the pipeline uses -- so your rating and the
sensor's are directly comparable:

| Layer | The question in short |
|---|---|
| Stated Problem | What does it say the problem is? Is that the real subject? |
| Feasibility Gap | Does the solution fit the problem? |
| Incentive Mapping | Who benefits if you believe this? Who pays? |
| Systemic Alignment | Do the actions produce the goal claimed? |
| Consequence Analysis | What if it's true? What if it's false? |
| Hidden Driver | What's missing that you'd need to check it? |
| Peripheral Signals | Timing, sourcing, who is quoted and who isn't |
| Feedback Loops | Does the pattern self-correct or self-reinforce? |

Plus five open questions with no rating. One is asked **before** you
read past the headline (what did you already believe?) and one is the
most diagnostic item on the sheet:

> What specific evidence would change your mind?

If nothing would, you are not evaluating the article -- you are
defending or dismissing it, and the other eight answers are theater.

### Reading the comparison

The ferret is **not** ground truth. It matches keywords and patterns
and has no idea what the article is about. So the three outcomes do
not mean what a grade would mean:

- **You rated higher.** Usually you are right. You can see structure --
  an argument that never names its actor, a solution mis-sized for its
  problem -- and the sensors only see vocabulary. What you saw is the
  finding. Write it down.

- **The ferret rated higher.** Read the matched phrases it prints.
  Either you missed loaded language, or the article uses a flagged
  vocabulary honestly. Only looking at the matches tells you which.

- **You agreed.** Weak evidence. A human and a keyword matcher can
  agree because the article is stylistically obvious.

Run it on `examples/offshore_wind_radar.txt` and you can watch the
sensors over-fire: Peripheral Signals goes RED on "Engineers say" and
"Veterans say", which are ordinary attribution verbs, and Systemic
Alignment goes RED on "budget" and "spending". That is not a bug to
work around -- it is the exercise. A reader who defers to the score
records eight REDs and learns nothing.

### There is no grade

The run ends in a calibration readout, not a score. Matching the
ferret perfectly would mean you had become a pattern matcher too.

## Offline use

`--worksheet` prints the entire check as plain text wrapped to 70
columns, with blanks to write in. No computer needed to do the
thinking part; the tool is only for the comparison afterward. Groups
can fill the same sheet on one article and compare with each other
before anyone runs anything.

## For contributors

`practice/` is deliberately **outside** `schema_contract`. It is
pedagogy, not a published interface, and it should be free to change
without a `SCHEMA_VERSION` bump. Its stability is documented by
`__all__` in `practice/__init__.py`.

The question bank is data (`LAYER_QUESTIONS`, `OPEN_QUESTIONS`) and
the comparison is a pure function of two dataclasses, so both are
testable without touching stdin. `tests/test_article_check.py` covers
the bank, the comparison, the blind-first ordering, and the worksheet.
