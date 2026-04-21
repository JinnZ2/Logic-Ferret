"""
Tests for the Logic-Ferret schema contract.

Standalone script -- no external runner. Run directly:
    python tests/test_schema_contract.py
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema_contract import (
    SCHEMA_VERSION,
    SENSOR_REGISTRY,
    LAYER_NAMES,
    SIGNAL_LEVELS,
    FALLACY_NAMES,
    SIGNATURES,
    SignatureMismatch,
    assert_signatures,
    GREEN, AMBER, RED, BLACK,
    TIER_LEVELS,
    SIGNAL_TO_TIER,
    CAMOUFLAGE_TIER_THRESHOLDS,
    DISCOURSE_COLLAPSE_MODES,
    ELEVATION_CLAUSES,
    REPORTAGE_DEESCALATED_SUFFIX,
    score_to_tier,
    layer_tiers,
    sensor_tiers,
    ferret_surface,
)


def test_schema_version_is_semver():
    print("[test_schema_version_is_semver]")
    parts = SCHEMA_VERSION.split(".")
    assert len(parts) == 3, f"not MAJOR.MINOR.PATCH: {SCHEMA_VERSION}"
    for p in parts:
        assert p.isdigit(), f"non-numeric semver component: {p}"
    print(f"  version = {SCHEMA_VERSION}")
    print("  PASS")


def test_sensor_registry_complete():
    print("[test_sensor_registry_complete]")
    assert len(SENSOR_REGISTRY) == 14, f"expected 14 sensors, got {len(SENSOR_REGISTRY)}"
    for name, fn in SENSOR_REGISTRY.items():
        assert callable(fn), f"{name} is not callable"
    assert "Discourse Collapse" in SENSOR_REGISTRY
    assert "Conflict Diagnosis" in SENSOR_REGISTRY
    print(f"  {len(SENSOR_REGISTRY)} sensors registered")
    print("  PASS")


def test_sensors_return_expected_shape():
    print("[test_sensors_return_expected_shape]")
    text = "We must act now because experts agree."
    for name, fn in SENSOR_REGISTRY.items():
        result = fn(text)
        assert isinstance(result, tuple) and len(result) == 2, f"{name}: bad return"
        score, flags = result
        assert isinstance(score, float), f"{name}: score not float"
        assert 0.0 <= score <= 1.0, f"{name}: score {score} out of [0,1]"
        assert isinstance(flags, dict), f"{name}: flags not dict"
    print(f"  all {len(SENSOR_REGISTRY)} sensors conform to (float, dict) contract")
    print("  PASS")


def test_tier_taxonomy():
    print("[test_tier_taxonomy]")
    assert TIER_LEVELS == (GREEN, AMBER, RED, BLACK)
    assert GREEN == "GREEN" and AMBER == "AMBER" and RED == "RED" and BLACK == "BLACK"
    assert SIGNAL_TO_TIER == {"strong": RED, "moderate": AMBER, "weak": GREEN}
    print("  PASS")


def test_score_to_tier_thresholds():
    print("[test_score_to_tier_thresholds]")
    cases = [
        (0.00, GREEN), (0.44, GREEN),
        (0.45, AMBER), (0.69, AMBER),
        (0.70, RED),   (1.00, RED),   (5.00, RED),
    ]
    for score, want in cases:
        got = score_to_tier(score)
        assert got == want, f"score_to_tier({score}) = {got}, want {want}"
    # never emits BLACK from score alone
    for s in (0.0, 0.5, 1.0, 99.0):
        assert score_to_tier(s) != BLACK, "score_to_tier must never return BLACK"
    print("  thresholds correct; BLACK never emitted from score alone")
    print("  PASS")


def test_discourse_collapse_vocabulary():
    print("[test_discourse_collapse_vocabulary]")
    assert DISCOURSE_COLLAPSE_MODES == (
        "semantic_inversion",
        "self_sealing",
        "action_licensing",
        "critical_thinking_suppression",
    )
    assert set(ELEVATION_CLAUSES) == {
        "none", "cognition_attack", "violence_coordination", "compounding"
    }
    assert REPORTAGE_DEESCALATED_SUFFIX == "__deescalated_reportage"
    print("  PASS")


def test_signatures_pinnable():
    print("[test_signatures_pinnable]")
    assert_signatures(SIGNATURES)
    assert_signatures({"assess": SIGNATURES["assess"]})  # partial pin
    print("  exact + partial pins both accepted")
    print("  PASS")


def test_signatures_detect_drift():
    print("[test_signatures_detect_drift]")
    try:
        assert_signatures({"assess": "(text: str) -> float"})
    except SignatureMismatch as e:
        assert "assess" in str(e)
        print(f"  drift raised as expected: {str(e).splitlines()[0]}")
        print("  PASS")
        return
    raise AssertionError("FAIL: drift was not detected")


def test_signatures_detect_missing_key():
    print("[test_signatures_detect_missing_key]")
    try:
        assert_signatures({"nonexistent_function": "(x) -> y"})
    except SignatureMismatch as e:
        assert "nonexistent_function" in str(e)
        print("  PASS")
        return
    raise AssertionError("FAIL: missing key not detected")


def test_ferret_surface_json_serializable():
    print("[test_ferret_surface_json_serializable]")
    surf = ferret_surface()
    # must round-trip through JSON
    serialized = json.dumps(surf)
    restored = json.loads(serialized)
    assert restored["schema_version"] == SCHEMA_VERSION
    required_keys = {
        "schema_version", "sensor_names", "layer_names", "signal_levels",
        "fallacy_names", "tier_levels", "signal_to_tier",
        "camouflage_tier_thresholds", "discourse_collapse_modes",
        "elevation_clauses", "reportage_deescalated_suffix",
        "black_elevation_policy", "signatures",
    }
    missing = required_keys - set(surf.keys())
    assert not missing, f"missing surface keys: {missing}"
    print(f"  {len(surf)} keys, {len(serialized)} bytes JSON, round-trips clean")
    print("  PASS")


def test_layer_tiers_covers_all_layers():
    print("[test_layer_tiers_covers_all_layers]")
    text = "The task force will study the issue. We must act for security reasons."
    tiers = layer_tiers(text)
    assert set(tiers.keys()) == set(LAYER_NAMES)
    for name, tier in tiers.items():
        assert tier in TIER_LEVELS, f"{name}: invalid tier {tier}"
    print(f"  {len(tiers)} layers, all valid tiers")
    print("  PASS")


def test_sensor_tiers_covers_all_sensors():
    print("[test_sensor_tiers_covers_all_sensors]")
    text = "Revenue grew last quarter."
    tiers = sensor_tiers(text)
    assert set(tiers.keys()) == set(SENSOR_REGISTRY.keys())
    for name, tier in tiers.items():
        assert tier in TIER_LEVELS, f"{name}: invalid tier {tier}"
        # sensor_tiers uses score_to_tier which never emits BLACK
        assert tier != BLACK, f"sensor_tiers emitted BLACK for {name} (impossible)"
    print(f"  {len(tiers)} sensors, all valid tiers, no BLACK (as designed)")
    print("  PASS")


if __name__ == "__main__":
    test_schema_version_is_semver()
    test_sensor_registry_complete()
    test_sensors_return_expected_shape()
    test_tier_taxonomy()
    test_score_to_tier_thresholds()
    test_discourse_collapse_vocabulary()
    test_signatures_pinnable()
    test_signatures_detect_drift()
    test_signatures_detect_missing_key()
    test_ferret_surface_json_serializable()
    test_layer_tiers_covers_all_layers()
    test_sensor_tiers_covers_all_sensors()
    print("\nall schema_contract tests passed.")
