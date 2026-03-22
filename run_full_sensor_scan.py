# run_full_sensor_scan.py

from sensor_suite.sensors import (
    propaganda_tone,
    reward_manipulation,
    false_urgency,
    gatekeeping,
    narrative_fragility,
    agency_restriction,
    propaganda_bias,
    fallacy_overlay,
    truth_integrity_score,
    gaslight_frequency,
    responsibility_deflection,
    true_accountability,
    meritocracy,
)
from typing import Dict
import sys

# (display_name, weight_key, sensor_function)
SENSORS = [
    ("🎭 Propaganda Tone", "Propaganda Tone", propaganda_tone.assess),
    ("💰 Reward Manipulation", "Reward Manipulation", reward_manipulation.assess),
    ("⏰ False Urgency", "False Urgency", false_urgency.assess),
    ("🔐 Gatekeeping", "Gatekeeping", gatekeeping.assess),
    ("📖 Narrative Fragility", "Narrative Fragility", narrative_fragility.assess),
    ("🧍 Agency Restriction", "Agency Restriction", agency_restriction.assess),
    ("🧿 Propaganda Bias", "Propaganda Bias", propaganda_bias.assess),
    ("🦝 Fallacy Overlay", "Fallacy Overlay", fallacy_overlay.assess),
    ("🔥 Gaslight Frequency", "Gaslight Frequency", gaslight_frequency.assess),
    ("🪞 Responsibility Deflection", "Responsibility Deflection", responsibility_deflection.assess),
    ("✅ True Accountability", "True Accountability", true_accountability.assess),
    ("🏅 Meritocracy", "Meritocracy", meritocracy.assess),
]

def run_all(text: str):
    sensor_results: Dict[str, float] = {}

    print("🧠 FULL SENSOR FUSION ANALYSIS\n" + "=" * 40)
    for display_name, key, sensor in SENSORS:
        try:
            score, flags = sensor(text)
            sensor_results[key] = score
            print(f"\n{display_name} Score: {score:.2f}")
            for k, v in flags.items():
                print(f"  - {k}: {v}")
        except Exception as e:
            print(f"⚠️  Error in {display_name}: {str(e)}")

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
