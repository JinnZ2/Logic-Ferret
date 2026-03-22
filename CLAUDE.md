# CLAUDE.md — Logic Ferret

## Project Overview

Logic Ferret is a sarcastic logical fallacy detector and "bullshit flagger" built in Python. It provides both a Tkinter GUI and a CLI interface to analyze text for logical fallacies, propaganda, manipulation tactics, and dishonest argumentation. Tagline: *"Spot the Nonsense. Smack the Source™"*

**Author:** JinnZ2
**License:** MIT

## Tech Stack

- **Language:** Python 3.8+
- **GUI:** Tkinter (bundled with Python)
- **Dependencies:** None beyond the standard library
- **Packaging:** setuptools (`setup.py`)

## Repository Structure

```
Logic-Ferret/
├── fallacy_gui.py                 # Primary entry point — Tkinter GUI app
├── run_full_sensor_scan.py        # CLI entry point — full sensor fusion analysis
├── setup.py                       # Package setup (console_scripts entry point)
├── __init__.py                    # Package init
├── .gitignore
├── sensor_suite/                  # Main analysis engine
│   ├── __init__.py
│   ├── weights.txt                # Sensor weight configuration and rationale
│   └── sensors/                   # Individual detection sensors (12 modules)
│       ├── __init__.py
│       ├── fallacy_overlay.py     # 7 logical fallacies (strawman, ad hominem, etc.)
│       ├── propaganda_tone.py     # Propaganda tone detection
│       ├── propaganda_bias.py     # Informative vs. persuasive language
│       ├── reward_manipulation.py # FOMO, social proof, emotional bribes
│       ├── false_urgency.py       # Hype language, fake countdowns
│       ├── gatekeeping.py         # Credentialism, jargon, access restrictions
│       ├── narrative_fragility.py # Weak transitions, evidence gaps
│       ├── agency_restriction.py  # Coercive framing, false choices
│       ├── gaslight_frequency.py  # Gaslighting patterns
│       ├── responsibility_deflection.py  # Blame shifting, credit stealing
│       ├── true_accountability.py # Accountability markers, humility (+)
│       ├── meritocracy.py         # Competence vs. false authority (+)
│       └── truth_integrity_score.py  # C3 composite score calculator
├── README.md
└── LICENSE
```

## Architecture

### Sensor Pattern

Every sensor module exposes a consistent interface:

```python
def assess(text: str) -> Tuple[float, Dict[str, Any]]:
    """
    Returns:
      - score: float 0.0–1.0 (higher = more problematic)
      - flags: dict with detailed metrics and matched patterns
    """
```

### Scoring Direction

- **Negative sensors** (10 of 12): Higher score = more distortion detected (bad)
- **Positive sensors** (true_accountability, meritocracy): Higher score = more positive signal (good)
- The C3 composite scorer automatically inverts positive sensors so they reduce the overall distortion score

### Composite Scoring (C3)

`truth_integrity_score.py` (in `sensor_suite/sensors/`) computes a Truth Integrity Composite Score using weighted averaging across all 12 sensors. Weights range from 1.0–1.6 and are defined in `WEIGHTS` dict in that file. See `sensor_suite/weights.txt` for rationale. Agency restriction is highest at 1.6.

### GUI (`fallacy_gui.py`)

- Dark-themed Tkinter window (1200x700)
- Input box for markdown-style transcripts with file loading
- "FLAG BULLSHIT" button triggers analysis
- Output: annotated transcript + fallacy count panel

### CLI (`run_full_sensor_scan.py`)

- Takes a text file path as argument
- Runs all 12 sensors sequentially
- Prints per-sensor scores, flags, and composite C3 score
- Uses (display_name, weight_key, sensor_fn) tuples to separate presentation from scoring

## Running the Project

```bash
# GUI
python fallacy_gui.py

# CLI sensor scan
python run_full_sensor_scan.py <path-to-text-file>

# Via setup.py install
pip install .
logic-ferret
```

## Development Guidelines

### Adding a New Sensor

1. Create a new file in `sensor_suite/sensors/` using snake_case (no suffix needed)
2. Implement `assess(text: str) -> Tuple[float, Dict]` following the existing pattern
3. Add a weight entry in `truth_integrity_score.py` WEIGHTS dict
4. If it's a positive sensor, add its key to POSITIVE_SENSORS
5. Add the sensor to the SENSORS list in `run_full_sensor_scan.py`
6. Document the weight rationale in `sensor_suite/weights.txt`

### Code Conventions

- Pure Python, no external dependencies — keep it that way
- Sensor modules are self-contained with their own keyword/pattern lists
- Scores are always 0.0–1.0 floats
- Flag dictionaries should include descriptive keys for what was detected
- File names use snake_case with no type suffix (no `_sensor`, `_detector`, `_meter`)
- Dark humor and sarcastic tone in user-facing strings is intentional and should be preserved

### Known Issues

- No test suite exists

### Testing

No testing framework is currently configured. There are no automated tests. When adding tests, `pytest` would be the recommended framework.

### CI/CD

No CI/CD pipeline is configured.

### Linting

No linter is configured. When adding one, `flake8` or `ruff` would be reasonable choices.
