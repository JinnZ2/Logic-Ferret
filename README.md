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

Author

Logic Ferret GUI™
A feral member of the [Logic Monk Stack], Jinn2Z.
Built for the tired minds who still believe truth matters.
