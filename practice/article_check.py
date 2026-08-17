"""
article_check.py -- a critical-thinking check a human runs on an article.

This is NOT another scorer. The sensor suite already scores text. This
is the other half: a structured read that YOU do, compared afterward
against what the sensors found, so you can see where your judgment and
the machine's pattern-matching diverge.

The order is the whole point. You answer first, blind. Then the ferret
answers. Then you compare.

Showing the score first would defeat the exercise -- you would read the
article looking for what the number told you to find. Anchoring is
cheap and it feels like insight. So `machine_read()` is not called
until a complete `HumanRead` exists.

WHAT THE COMPARISON MEANS

The ferret is not ground truth. It is a keyword and pattern matcher,
and it has no idea what the article is about. So:

  - You rated higher than the ferret. Usually YOU are right. You can
    read structure -- an argument that never names its actor, a
    solution that does not fit its stated problem -- and the sensors
    only see vocabulary. Write down what you saw; that is the finding.

  - The ferret rated higher than you. Go back and look at the phrases
    it matched. Either you missed loaded language, or the article uses
    a flagged vocabulary honestly (a real emergency does contain
    urgency words). Both outcomes are worth knowing, and only reading
    the matches tells you which.

  - You agreed. Weak evidence. Agreement between a human reader and a
    keyword matcher can just mean the article is stylistically obvious.
    It is not confirmation.

There is no grade at the end. A calibration readout is not a score,
and treating it as one would reproduce the exact failure the rest of
this repo is built to detect.

License: CC0
"""
import textwrap
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from schema_contract import LAYER_NAMES, TIER_LEVELS, SIGNAL_TO_TIER

WIDTH = 70

__all__ = [
    "LayerQuestion",
    "OpenQuestion",
    "LAYER_QUESTIONS",
    "OPEN_QUESTIONS",
    "RATING_SCALE",
    "HumanRead",
    "MachineRead",
    "Divergence",
    "tier_rank",
    "machine_read",
    "compare",
    "format_report",
    "blank_worksheet",
]


# ============================================================
# THE RATING SCALE
# ============================================================

# Deliberately the same four tiers the rest of the repo uses, so a
# human rating and a sensor rating are directly comparable. BLACK is
# reachable only on the overall estimate, not per layer -- same rule
# the pipeline follows (only Layer 9 can elevate to BLACK).
RATING_SCALE = {
    "GREEN": "Clear. The article addresses this honestly, or it does not apply.",
    "AMBER": "Vague, partial, or unexamined. Something is being skipped.",
    "RED": "Actively misleading here. The framing works against understanding.",
    "BLACK": "(overall only) Not an argument -- reasoning itself is under attack.",
}


# ============================================================
# THE EIGHT LAYER QUESTIONS
# ============================================================

@dataclass(frozen=True)
class LayerQuestion:
    """One question per diagnosis layer, phrased for a human reader.

    `layer` matches a name in schema_contract.LAYER_NAMES so the answer
    can be compared directly against that layer's sensor signal.
    """

    layer: str
    ask: str
    looking_for: str
    green_looks_like: str
    red_looks_like: str


LAYER_QUESTIONS: Tuple[LayerQuestion, ...] = (
    LayerQuestion(
        layer="Stated Problem",
        ask=(
            "In one sentence, what does this article say the problem is? "
            "Use its own words. Then ask: is that the actual subject, or "
            "is it the frame you have been handed?"
        ),
        looking_for=(
            "The gap between the problem named in the headline and the "
            "problem the body of the article is actually about. Writing "
            "the stated problem down in one sentence is what exposes it -- "
            "if you cannot, that is the finding."
        ),
        green_looks_like="The problem is stated plainly and the article stays on it.",
        red_looks_like=(
            "The stated problem is a proxy for an unstated one, or it shifts "
            "between the headline and the middle paragraphs."
        ),
    ),
    LayerQuestion(
        layer="Feasibility Gap",
        ask=(
            "Does the proposed solution actually fit the stated problem? "
            "What would have to be true for it to work?"
        ),
        looking_for=(
            "Solutions sized wrong for their problem. A measure that "
            "addresses 2% of a thing described as a crisis. A fix whose "
            "preconditions are never mentioned."
        ),
        green_looks_like="The solution is proportionate and its preconditions are stated.",
        red_looks_like=(
            "The solution cannot produce the outcome claimed, and the article "
            "does not notice or does not say."
        ),
    ),
    LayerQuestion(
        layer="Incentive Mapping",
        ask=(
            "Who benefits if you believe this? Who pays? Name them "
            "specifically -- not 'corporations', an actual party."
        ),
        looking_for=(
            "Whether the article lets you identify interested parties at all. "
            "Vagueness about who gains is itself the signal."
        ),
        green_looks_like="Interests are disclosed, including the publisher's own.",
        red_looks_like=(
            "You cannot name a single beneficiary from the text, or the "
            "obvious one goes unmentioned."
        ),
    ),
    LayerQuestion(
        layer="Systemic Alignment",
        ask=(
            "Do the actions described actually produce the goal claimed? "
            "Track the stated goal against what is being done, not what is "
            "being said about it."
        ),
        looking_for=(
            "Performance versus outcome. Announcements counted as results. "
            "Process described where effect was promised."
        ),
        green_looks_like="Actions and stated goal point the same direction.",
        red_looks_like="The activity described would not move the stated goal at all.",
    ),
    LayerQuestion(
        layer="Consequence Analysis",
        ask=(
            "What happens next if this is true? What happens if it is false? "
            "Does the article engage either?"
        ),
        looking_for=(
            "Articles that assert without following through. If being wrong "
            "costs the author nothing, the claim was cheap to make."
        ),
        green_looks_like="Both branches are considered, including the cost of being wrong.",
        red_looks_like="Only one future is imaginable and no cost of error is named.",
    ),
    LayerQuestion(
        layer="Hidden Driver",
        ask=(
            "What is the article not saying? What would you need to know to "
            "check its central claim yourself?"
        ),
        looking_for=(
            "The missing denominator. The unnamed comparison group. The "
            "number given as a percentage when the raw count would deflate it."
        ),
        green_looks_like="You could check the main claim from what is given.",
        red_looks_like=(
            "Checking the claim requires information the article had and "
            "chose not to include."
        ),
    ),
    LayerQuestion(
        layer="Peripheral Signals",
        ask=(
            "What is happening in the margins -- the timing, the sourcing, "
            "who is quoted directly, who is described but never quoted, what "
            "got put in the last paragraph?"
        ),
        looking_for=(
            "Placement as argument. The correction buried at the bottom, the "
            "critic paraphrased while the defender is quoted directly, the "
            "release timed to a news cycle."
        ),
        green_looks_like="Sourcing is even-handed and placement is not doing work.",
        red_looks_like="The structure argues a case the text does not defend openly.",
    ),
    LayerQuestion(
        layer="Feedback Loops",
        ask=(
            "If the pattern this article describes continues, does it "
            "self-correct or self-reinforce?"
        ),
        looking_for=(
            "Whether the situation contains a mechanism that would fix it. "
            "Self-reinforcing patterns get described as stable right up until "
            "they are not."
        ),
        green_looks_like="A correcting mechanism exists and is named.",
        red_looks_like=(
            "The pattern feeds itself and the article treats it as a "
            "steady state."
        ),
    ),
)


# ============================================================
# THE OPEN QUESTIONS (no rating -- you write an answer)
# ============================================================

@dataclass(frozen=True)
class OpenQuestion:
    key: str
    ask: str
    why: str


OPEN_QUESTIONS: Tuple[OpenQuestion, ...] = (
    OpenQuestion(
        key="prior",
        ask=(
            "Before you read past the headline: what did you already believe "
            "about this topic? Write it down now."
        ),
        why=(
            "Answered last, this is a rationalization. Answered first, it is "
            "the only way to tell later whether the article informed you or "
            "just agreed with you."
        ),
    ),
    OpenQuestion(
        key="falsifiable",
        ask=(
            "What specific evidence would change your mind about this "
            "article's main claim?"
        ),
        why=(
            "The single most diagnostic question here. If nothing would "
            "change your mind, you are not evaluating the article -- you are "
            "defending or dismissing it, and the other questions are theater."
        ),
    ),
    OpenQuestion(
        key="steelman",
        ask=(
            "State the strongest honest version of the case this article "
            "argues against. Strong enough that someone holding it would "
            "recognize themselves."
        ),
        why=(
            "If you can only reproduce the article's version of the "
            "opposition, you have absorbed its framing rather than assessed "
            "it."
        ),
    ),
    OpenQuestion(
        key="scope",
        ask=(
            "What population, place, and time period does the main claim "
            "actually cover? Compare that to how broadly it is stated."
        ),
        why=(
            "Most misapplication is scope drift, not fabrication. A true "
            "finding applied outside the conditions that produced it is "
            "still wrong. See knowledge/study_scope_audit.py."
        ),
    ),
    OpenQuestion(
        key="sources",
        ask=(
            "Who is quoted? Who is described but never quoted? Who would you "
            "need to hear from to settle this?"
        ),
        why=(
            "The third list is usually the shortest to write and the most "
            "revealing. It names what the article decided you did not need."
        ),
    ),
)


# ============================================================
# READS
# ============================================================

def _wrap(text: str, indent: str = "", first: str = None) -> List[str]:
    """Wrap to WIDTH so the worksheet prints on paper without reflowing."""
    return textwrap.wrap(
        " ".join(text.split()),
        width=WIDTH,
        initial_indent=indent if first is None else first,
        subsequent_indent=indent,
    ) or [indent.rstrip()]


def tier_rank(tier: str) -> int:
    """Position in TIER_LEVELS. Raises on an unknown tier."""
    try:
        return TIER_LEVELS.index(tier)
    except ValueError:
        raise ValueError(
            f"unknown tier {tier!r}; expected one of {list(TIER_LEVELS)}"
        ) from None


@dataclass
class HumanRead:
    """What the reader concluded, recorded before any machine output."""

    layer_ratings: Dict[str, str]
    overall: str
    answers: Dict[str, str] = field(default_factory=dict)
    notes: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        missing = [name for name in LAYER_NAMES if name not in self.layer_ratings]
        if missing:
            raise ValueError(f"no rating recorded for: {missing}")

        unknown = [name for name in self.layer_ratings if name not in LAYER_NAMES]
        if unknown:
            raise ValueError(f"not a diagnosis layer: {unknown}")

        for name, rating in self.layer_ratings.items():
            if rating == "BLACK":
                raise ValueError(
                    f"{name}: BLACK is an overall rating only -- per layer, "
                    f"the ceiling is RED (only discourse collapse reaches BLACK)"
                )
            tier_rank(rating)
        tier_rank(self.overall)


@dataclass
class MachineRead:
    """What the sensors found. Built only from diagnose() output."""

    layer_tiers: Dict[str, str]
    layer_hits: Dict[str, int]
    layer_matches: Dict[str, List[str]]
    overall: str
    camouflage_score: float
    collapse_alert: bool


def machine_read(text: str) -> MachineRead:
    """Run the 9-layer pipeline and reduce it to per-layer tiers.

    Imported lazily so that generating a blank worksheet -- the offline,
    no-computer path -- does not require the sensor suite to load.
    """
    from sensor_suite.sensors.conflict_diagnosis import diagnose

    result = diagnose(text)

    layer_tiers: Dict[str, str] = {}
    layer_hits: Dict[str, int] = {}
    layer_matches: Dict[str, List[str]] = {}
    for entry in result["layers"]:
        name = entry["layer"]
        layer_tiers[name] = SIGNAL_TO_TIER[entry["signal"]]
        layer_hits[name] = entry["hits"]
        layer_matches[name] = list(entry["matches"])[:5]

    return MachineRead(
        layer_tiers=layer_tiers,
        layer_hits=layer_hits,
        layer_matches=layer_matches,
        overall=result["tier"],
        camouflage_score=result["camouflage_score"],
        collapse_alert=bool(result["discourse_collapse"].get("alert", False)),
    )


# ============================================================
# COMPARISON
# ============================================================

AGREE = "agree"
YOU_SAW_MORE = "you_saw_more"
FERRET_SAW_MORE = "ferret_saw_more"


@dataclass
class Divergence:
    layer: str
    human: str
    machine: str
    kind: str
    distance: int
    hits: int
    matches: List[str]

    def explain(self) -> str:
        if self.kind == AGREE:
            return (
                "Agreed. Weak evidence -- a keyword matcher and a human can "
                "agree because the article is stylistically obvious."
            )
        if self.kind == YOU_SAW_MORE:
            return (
                "You rated this higher. The sensors match vocabulary, not "
                "structure, so this is often a real catch they cannot make. "
                "Write down what you saw."
            )
        return (
            f"The ferret rated this higher ({self.hits} pattern hit(s)). "
            f"Read the matched phrases below: either you missed loaded "
            f"language, or this article uses a flagged vocabulary honestly."
        )


def compare(human: HumanRead, machine: MachineRead) -> List[Divergence]:
    """Per-layer comparison, ordered most-divergent first."""
    human.validate()

    divergences: List[Divergence] = []
    for name in LAYER_NAMES:
        h = human.layer_ratings[name]
        m = machine.layer_tiers.get(name, "GREEN")
        delta = tier_rank(h) - tier_rank(m)
        if delta == 0:
            kind = AGREE
        elif delta > 0:
            kind = YOU_SAW_MORE
        else:
            kind = FERRET_SAW_MORE
        divergences.append(
            Divergence(
                layer=name,
                human=h,
                machine=m,
                kind=kind,
                distance=abs(delta),
                hits=machine.layer_hits.get(name, 0),
                matches=machine.layer_matches.get(name, []),
            )
        )

    divergences.sort(key=lambda d: (-d.distance, LAYER_NAMES.index(d.layer)))
    return divergences


# ============================================================
# REPORT
# ============================================================

def format_report(human: HumanRead, machine: MachineRead) -> str:
    divergences = compare(human, machine)

    agreed = [d for d in divergences if d.kind == AGREE]
    you = [d for d in divergences if d.kind == YOU_SAW_MORE]
    ferret = [d for d in divergences if d.kind == FERRET_SAW_MORE]

    lines = [
        "=" * 70,
        "ARTICLE CHECK -- YOUR READ vs THE FERRET'S",
        "=" * 70,
        "",
        f"  Your overall estimate : {human.overall}",
        f"  Ferret tier           : {machine.overall} "
        f"(camouflage {machine.camouflage_score:.2f})",
    ]
    if machine.collapse_alert:
        lines.append(
            "  DISCOURSE COLLAPSE ALERT -- Layer 9 fired. This is the only "
            "path to BLACK."
        )
    lines.append("")

    if human.overall != machine.overall:
        lines.extend(
            _wrap(
                f"You and the ferret disagree at the top line "
                f"({human.overall} vs {machine.overall}). That disagreement "
                f"is the most useful output on this page. Neither reading is "
                f"authoritative; find out which one the text supports.",
                indent="  ",
            )
        )
    else:
        lines.extend(
            _wrap(
                f"You and the ferret both landed on {human.overall}. Do not "
                f"take that as confirmation -- see the per-layer breakdown.",
                indent="  ",
            )
        )
    lines.append("")

    lines.append("-" * 70)
    lines.append("PER LAYER (most divergent first)")
    lines.append("-" * 70)
    for d in divergences:
        marker = {AGREE: "=", YOU_SAW_MORE: ">", FERRET_SAW_MORE: "<"}[d.kind]
        lines.append("")
        lines.append(f"  [{marker}] {d.layer}")
        lines.append(f"      you: {d.human:<6} ferret: {d.machine}")
        lines.extend(_wrap(d.explain(), indent="      "))
        if d.kind == FERRET_SAW_MORE and d.matches:
            lines.append("      matched:")
            for phrase in d.matches:
                collapsed = " ".join(str(phrase).split())
                if len(collapsed) > 60:
                    collapsed = collapsed[:57] + "..."
                lines.append(f"        - {collapsed}")

    lines.extend(["", "-" * 70, "CALIBRATION READOUT", "-" * 70])
    lines.append(f"  agreed              : {len(agreed)} of {len(LAYER_NAMES)}")
    lines.append(f"  you saw more        : {len(you)}")
    lines.append(f"  ferret saw more     : {len(ferret)}")
    lines.append("")
    lines.append("  This is not a grade. The ferret is a pattern matcher with")
    lines.append("  no understanding of the article. Matching it perfectly")
    lines.append("  would mean you had become a pattern matcher too.")

    if human.answers.get("falsifiable", "").strip():
        lines.extend(["", "-" * 70, "YOUR ANSWER THAT MATTERS MOST", "-" * 70])
        lines.append("  What would change your mind:")
        lines.append(f"    {human.answers['falsifiable'].strip()}")
        lines.append("")
        lines.append("  Hold onto that. If you meet it later and do not move,")
        lines.append("  the answer was decorative.")
    else:
        lines.extend(["", "-" * 70])
        lines.append("  You left 'what would change your mind' blank.")
        lines.append("  That is the one question worth going back for.")

    lines.extend(["", "=" * 70])
    return "\n".join(lines)


# ============================================================
# BLANK WORKSHEET (printable, no computer needed)
# ============================================================

def blank_worksheet(title: str = "") -> str:
    """The whole check as plain text, for printing or classroom use."""
    lines = [
        "=" * 70,
        "ARTICLE CHECK -- WORKSHEET",
        "=" * 70,
    ]
    if title:
        lines.append(f"Article: {title}")
    lines.append("")
    lines.extend(
        _wrap(
            "Answer everything before running any tool on this article. The "
            "comparison only means something if your read came first."
        )
    )
    lines.extend(["", "RATING SCALE"])
    for tier, meaning in RATING_SCALE.items():
        lines.extend(_wrap(meaning, indent=" " * 9, first=f"  {tier:<6} "))

    lines.extend(["", "-" * 70, "FIRST -- before you read past the headline", "-" * 70])
    prior = OPEN_QUESTIONS[0]
    lines.append("")
    lines.extend(_wrap(prior.ask, indent="  "))
    lines.extend(_wrap(f"({prior.why})", indent="    "))
    lines.extend(["", "    " + "_" * 60])

    lines.extend(["", "-" * 70, "THE EIGHT LAYERS", "-" * 70])
    for i, q in enumerate(LAYER_QUESTIONS, start=1):
        lines.extend(["", f"{i}. {q.layer.upper()}"])
        lines.extend(_wrap(q.ask, indent="   "))
        lines.append("")
        lines.extend(_wrap(q.looking_for, indent="   ", first="   Looking for: "))
        lines.extend(_wrap(q.green_looks_like, indent="          ", first="   GREEN: "))
        lines.extend(_wrap(q.red_looks_like, indent="          ", first="   RED:   "))
        lines.extend(
            [
                "",
                "   Rating (GREEN / AMBER / RED): ______",
                "   What you saw:",
                "     " + "_" * 60,
                "     " + "_" * 60,
            ]
        )

    lines.extend(["", "-" * 70, "AFTER READING", "-" * 70])
    for q in OPEN_QUESTIONS[1:]:
        lines.append("")
        lines.extend(_wrap(q.ask, indent="  "))
        lines.extend(_wrap(f"({q.why})", indent="    "))
        lines.extend(["", "    " + "_" * 60, "    " + "_" * 60])

    lines.extend(
        [
            "",
            "-" * 70,
            "OVERALL",
            "-" * 70,
            "",
            "  Your overall estimate (GREEN / AMBER / RED / BLACK): ______",
            "",
            "  Now, and only now, run:",
            "      python run_article_check.py <article.txt>",
            "",
        ]
    )
    lines.extend(
        _wrap(
            "Enter the ratings you already wrote down. The tool will show you "
            "where you and the sensors disagree. Disagreement is the point -- "
            "it tells you where to look again. Neither of you is the "
            "authority.",
            indent="  ",
        )
    )
    lines.append("=" * 70)
    return "\n".join(lines)


if __name__ == "__main__":
    print(blank_worksheet())
