# run_article_check.py
# ============================================================
# Critical-thinking check for a human reading an article.
#
# You answer first, blind. Then the ferret answers. Then you compare.
#
# Usage:
#   python run_article_check.py <article.txt>              interactive
#   python run_article_check.py --worksheet [> sheet.txt]  printable blank
#   python run_article_check.py <article.txt> --answers a.json
#
# The --answers form replays a saved read without prompting, so you can
# record a read on paper first and enter it afterward. Format:
#
#   {
#     "overall": "AMBER",
#     "layers":  {"Stated Problem": "RED", ...all eight...},
#     "answers": {"falsifiable": "...", "steelman": "..."}
#   }
# ============================================================

import json
import sys

from practice.article_check import (
    LAYER_QUESTIONS,
    OPEN_QUESTIONS,
    RATING_SCALE,
    HumanRead,
    blank_worksheet,
    format_report,
    machine_read,
)

VALID_LAYER = ("GREEN", "AMBER", "RED")
VALID_OVERALL = ("GREEN", "AMBER", "RED", "BLACK")


def usage() -> None:
    print("Logic Ferret -- Article Check")
    print('"You answer first. Then the ferret answers. Then you compare."')
    print()
    print("Usage:")
    print("  python run_article_check.py <article.txt>")
    print("  python run_article_check.py --worksheet")
    print("  python run_article_check.py <article.txt> --answers <read.json>")
    print()
    print("Options:")
    print("  --worksheet        Print a blank worksheet and exit")
    print("  --answers <file>   Replay a saved read instead of prompting")


def ask_rating(prompt: str, valid) -> str:
    """Prompt until a valid tier is given. Blank is not accepted --
    an unrated layer would silently become agreement."""
    options = "/".join(valid)
    while True:
        try:
            raw = input(f"{prompt} ({options}): ").strip().upper()
        except EOFError:
            print("\nInput ended before the read was complete. Nothing scored.")
            sys.exit(1)
        if raw in valid:
            return raw
        print(f"  Enter one of: {options}")


def ask_text(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def interactive_read() -> HumanRead:
    print("=" * 70)
    print("YOUR READ -- do this before the ferret says anything")
    print("=" * 70)
    print()
    for tier, meaning in RATING_SCALE.items():
        print(f"  {tier:<6} {meaning}")
    print()

    answers = {}
    notes = {}

    prior = OPEN_QUESTIONS[0]
    print("-" * 70)
    print(f"{prior.ask}")
    print(f"  ({prior.why})")
    answers[prior.key] = ask_text("> ")
    print()

    layer_ratings = {}
    for i, q in enumerate(LAYER_QUESTIONS, start=1):
        print("-" * 70)
        print(f"{i}. {q.layer.upper()}")
        print(f"   {q.ask}")
        print()
        print(f"   Looking for: {q.looking_for}")
        print(f"   GREEN: {q.green_looks_like}")
        print(f"   RED:   {q.red_looks_like}")
        print()
        notes[q.layer] = ask_text("   What you saw: ")
        layer_ratings[q.layer] = ask_rating("   Rating", VALID_LAYER)
        print()

    print("-" * 70)
    print("AFTER READING")
    print("-" * 70)
    for q in OPEN_QUESTIONS[1:]:
        print()
        print(f"{q.ask}")
        print(f"  ({q.why})")
        answers[q.key] = ask_text("> ")

    print()
    print("-" * 70)
    overall = ask_rating("Your overall estimate", VALID_OVERALL)
    print()

    return HumanRead(
        layer_ratings=layer_ratings,
        overall=overall,
        answers=answers,
        notes=notes,
    )


def load_read(path: str) -> HumanRead:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for key in ("overall", "layers"):
        if key not in data:
            print(f"{path}: missing required key {key!r}")
            sys.exit(1)
    return HumanRead(
        layer_ratings=data["layers"],
        overall=data["overall"],
        answers=data.get("answers", {}),
        notes=data.get("notes", {}),
    )


def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        usage()
        sys.exit(0)

    if args[0] == "--worksheet":
        print(blank_worksheet())
        return

    filepath = args[0]
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        sys.exit(1)

    if not text.strip():
        print("Empty file. The ferret needs something to sniff.")
        sys.exit(1)

    if "--answers" in args:
        idx = args.index("--answers")
        if idx + 1 >= len(args):
            print("--answers needs a file path")
            sys.exit(1)
        human = load_read(args[idx + 1])
    else:
        human = interactive_read()

    try:
        human.validate()
    except ValueError as exc:
        print(f"Incomplete read: {exc}")
        sys.exit(1)

    # Only now does the machine get to speak.
    print(format_report(human, machine_read(text)))


if __name__ == "__main__":
    main()
