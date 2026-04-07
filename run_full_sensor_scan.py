# run_full_sensor_scan.py
# Full sensor fusion analysis -- every sensor, one pass.

from sensor_suite.sensors import (
    propaganda_tone,
    reward_manipulation,
    false_urgency,
    gatekeeping_sensor,
    narrative_fragility,
    agency_detector,
    propaganda_bias,
    logic_fallacy_ferret,
    gaslight_frequency_meter,
    responsibility_deflection_sensor,
    true_accountability_sensor,
    meritocracy_detector,
    conflict_diagnosis,
    truth_integrity_score,
)
from typing import Dict
import sys

SENSORS = [
    ("Propaganda Tone", propaganda_tone.assess),
    ("Reward Manipulation", reward_manipulation.assess),
    ("False Urgency", false_urgency.assess),
    ("Gatekeeping", gatekeeping_sensor.assess),
    ("Narrative Fragility", narrative_fragility.assess),
    ("Agency Score", agency_detector.assess),
    ("Propaganda Bias", propaganda_bias.assess),
    ("Logic Fallacy Ferret", logic_fallacy_ferret.assess),
    ("Gaslight Frequency", gaslight_frequency_meter.assess),
    ("Responsibility Deflection", responsibility_deflection_sensor.assess),
    ("True Accountability", true_accountability_sensor.assess),
    ("Meritocracy Detector", meritocracy_detector.assess),
    ("Conflict Diagnosis", conflict_diagnosis.assess),
]


def run_all(text: str):
    sensor_results: Dict[str, float] = {}

    print("FULL SENSOR FUSION ANALYSIS\n" + "=" * 50)
    for name, sensor in SENSORS:
        try:
            score, flags = sensor(text)
            sensor_results[name] = score
            print(f"\n{name} Score: {score:.2f}")
            for k, v in flags.items():
                print(f"  - {k}: {v}")
        except Exception as e:
            print(f"  Error in {name}: {str(e)}")

    # Composite Score
    print("\nCalculating Composite Truth Integrity Score...")
    try:
        c3_score, weighted_breakdown = truth_integrity_score.calculate_c3(sensor_results)
        print(f"\nC3 Score (Truth Integrity): {c3_score:.2f}\n")
        print("Weighted Contributions:")
        for k, v in weighted_breakdown.items():
            print(f"  - {k}: {v:.3f}")
    except Exception as e:
        print(f"  Error calculating C3 Score: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_full_sensor_scan.py path/to/text.txt")
        sys.exit(1)

    try:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            content = f.read()
            run_all(content)
    except FileNotFoundError:
        print("File not found.")
