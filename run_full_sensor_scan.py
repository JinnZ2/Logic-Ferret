# /run_full_sensor_scan.py

from sensor_suite.sensors import (
    propaganda_tone,
    reward_manipulation,
    false_urgency,
    gatekeeping_sensor,
    narrative_fragility,
    agency_detector,
    propaganda_bias,
    fallacy_overlay,
    truth_integrity_score,
    gaslight_frequency_meter,
    responsibility_deflection_sensor,
    true_accountability_sensor,
    meritocracy_detector,
)
from typing import Dict
import sys

SENSORS = [
    ("🎭 Propaganda Tone", propaganda_tone.assess),
    ("💰 Reward Manipulation", reward_manipulation.assess),
    ("⏰ False Urgency", false_urgency.assess),
    ("🔐 Gatekeeping", gatekeeping_sensor.assess),
    ("📖 Narrative Fragility", narrative_fragility.assess),
    ("🧍 Agency Score", agency_detector.assess),
    ("🧿 Propaganda Bias", propaganda_bias.assess),
    ("🔥 Gaslight Frequency Meter", gaslight_frequency_meter.assess),
    ("🪞 Responsibility Deflection", responsibility_deflection_sensor.assess),
    ("✅ True Accountability", true_accountability_sensor.assess),
    ("🏅 Meritocracy Detector", meritocracy_detector.assess),
]

def run_all(text: str):
    sensor_results: Dict[str, float] = {}

    print("🧠 FULL SENSOR FUSION ANALYSIS\n" + "=" * 40)
    for name, sensor in SENSORS:
        try:
            score, flags = sensor(text)
            sensor_results[name] = score
            print(f"\n{name} Score: {score:.2f}")
            for k, v in flags.items():
                print(f"  - {k}: {v}")
        except Exception as e:
            print(f"⚠️  Error in {name}: {str(e)}")

    # Composite Score
    print("\n🧮 Calculating Composite Truth Integrity Score...")
    try:
        c3_score, weighted_breakdown = truth_integrity_score.calculate_c3(sensor_results)
        print(f"\n🔥 C3 Score (Truth Integrity): {c3_score:.2f}\n")
        print("🧾 Weighted Contributions:")
        for k, v in weighted_breakdown.items():
            print(f"  - {k}: {v:.3f}")
    except Exception as e:
        print(f"⚠️ Error calculating C3 Score: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_full_sensor_scan.py path/to/text.txt")
        sys.exit(1)

    try:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            content = f.read()
            run_all(content)
    except FileNotFoundError:
        print("❌ File not found.")
