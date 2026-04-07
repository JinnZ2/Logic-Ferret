# Logic-Ferret
Spot the Nonsense. Smack the Source._™  A beautifully sarcastic fallacy flagger and bullshit detector. Built for anyone who’s tired of pretending bad logic is okay.

Features
	•	 Tkinter GUI (simple, native Python)
	•	 Markdown-style transcript input
	•	 Scrollable annotated viewer
	•	 Fallacy frequency panel
	•	 FLAG BULLSHIT button (with tooltip, because obviously)

Quick Start

  Install Requirements:
  pip install -r requirements.txt

Run the App:

cd logic-ferret-gui/gui
python fallacy_gui.py

Sample Output
	•	Input a text transcript (manually or via file).
	•	Click  FLAG BULLSHIT.
	•	Watch as logical fallacies are auto-highlighted and counted like candy at a toddler’s birthday.

⸻

 Dependencies
	•	Python 3.8+
	•	Tkinter (comes with Python)
	•	Your custom annotate_text() function in:
sensor_suite/sensors/fallacy_overlay.py

def annotate_text(text: str) -> Tuple[str, Dict[str, int]]:
    """
    Detect fallacies in the given text.
    Returns:
      - Annotated text with tags/highlights
      - Dict of fallacy type -> count
    """

    If you want the button tooltip to say something like:

“Deploying your inner Socrates… Stand back.”

You can enhance the button using Hovertip (Python 3.9+)

from idlelib.tooltip import Hovertip
Hovertip(flag_button, "Deploying your inner Socrates… Stand back.")

If you’d like to run fallacy_gui.py as logic-ferret from terminal, you can wrap its launch in a main() function:

# Add to bottom of gui/fallacy_gui.py

def main():
    root.mainloop()

if __name__ == "__main__":
    main()


Sibling Framework

[Thermodynamic Accountability Framework (TAF)](https://github.com/JinnZ2/thermodynamic-accountability-framework) — measures institutional failure through physics. Logic Ferret measures it through rhetoric. TAF asks "does the energy math close?" while the Ferret asks "is the narrative camouflage?" Run both and the bullshit has nowhere left to hide.

| TAF Module | Logic Ferret Sensor | Shared Diagnostic |
|---|---|---|
| Narrative Stripper | Stated Problem + Feasibility Gap | Strip the story, check if it holds |
| Social Overhead Accountant | Systemic Alignment | Performance theater vs. actual outcomes |
| Root Cause Depth Analyzer | Hidden Driver + Consequences | Trace past symptoms to structure |
| Friction Ratio | Camouflage Score | Single number: how much is waste/cover? |
| Energy Conservation | Consequence divergence | Promised output vs. actual output |
| Entropy growth | Feedback Loops | Self-reinforcing decay the system won't fix |

Author

Logic Ferret GUI™
A feral member of the [Logic Monk Stack], Jinn2Z.
Built for the tired minds who still believe truth matters.
