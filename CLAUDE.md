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
├── Logic_fallacy_ferret.py        # Simple wrapper calling fallacy_overlay.assess()
├── truth_integrity_score.py       # Root-level scoring placeholder
├── setup.py                       # Package setup (console_scripts entry point)
├── __init__.py                    # Package init
├── sensor_suite/                  # Main analysis engine
│   ├── propaganda_tone.py         # Propaganda tone detection
│   ├── weights.txt                # Sensor weight configuration
│   └── sensors/                   # Individual detection sensors (11 modules)
│       ├── fallacy_overlay.py     # 7 logical fallacies (strawman, ad hominem, etc.)
│       ├── propaganda_bias.py     # Informative vs. persuasive language
│       ├── reward_manipulation.py # FOMO, social proof, emotional bribes
│       ├── false_urgency.py       # Hype language, fake countdowns
│       ├── gatekeeping_sensor.py  # Credentialism, jargon, access restrictions
│       ├── narrative_fragility.py # Weak transitions, evidence gaps
│       ├── agency_detector.py     # Coercive framing, false choices
│       ├── gaslight_frequency_meter.py      # Gaslighting patterns
│       ├── responsibility_deflection_sensor.py  # Blame shifting, credit stealing
│       ├── true_accountability_sensor.py    # Accountability markers, humility
│       └── truth_integrity_score.py         # C3 composite score calculator
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

### Composite Scoring (C3)

`truth_integrity_score.py` (in `sensor_suite/sensors/`) computes a Truth Integrity Composite Score using weighted averaging. Weights are defined in `sensor_suite/weights.txt` (range: 1.0–1.6; agency restriction is highest at 1.6).

### GUI (`fallacy_gui.py`)

- Dark-themed Tkinter window (1200x700)
- Input box for markdown-style transcripts with file loading
- "FLAG BULLSHIT" button triggers analysis
- Output: annotated transcript + fallacy count panel

### CLI (`run_full_sensor_scan.py`)

- Takes a text file path as argument
- Runs all 11 sensors sequentially
- Prints per-sensor scores, flags, and composite C3 score

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

1. Create a new file in `sensor_suite/sensors/`
2. Implement `assess(text: str) -> Tuple[float, Dict]` following the existing pattern
3. Add a weight entry in `sensor_suite/weights.txt`
4. Register the sensor import in `run_full_sensor_scan.py`

### Code Conventions

- Pure Python, no external dependencies — keep it that way
- Sensor modules are self-contained with their own keyword/pattern lists
- Scores are always 0.0–1.0 floats
- Flag dictionaries should include descriptive keys for what was detected
- Dark humor and sarcastic tone in user-facing strings is intentional and should be preserved

### Known Issues

- `sensor_suite/` and `sensor_suite/sensors/` are missing `__init__.py` files, which can cause import failures
- `reward_manipulation.py` has syntax errors (spaces in variable names)
- `responsibility_deflection_sensor.py` contains markdown formatting mixed with Python code
- `run_full_sensor_scan.py` has import syntax issues
- No test suite exists

### Testing

No testing framework is currently configured. There are no automated tests. When adding tests, `pytest` would be the recommended framework.

### CI/CD

No CI/CD pipeline is configured.

### Linting

No linter is configured. When adding one, `flake8` or `ruff` would be reasonable choices.
