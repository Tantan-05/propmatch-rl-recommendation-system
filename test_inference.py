"""
test_inference.py
=================
Test suite for inference.py — loads real assets, calls the live inference
function, and verifies correctness of results.

All tests use the real preprocessor and model weights.
Nothing is written or modified by this script.

Run:
    python test_inference.py
"""

from __future__ import annotations

import math
import sys
import warnings
from pathlib import Path

# ------------------------------------------------------------------ #
# Lightweight test framework (no pytest dependency required)
# ------------------------------------------------------------------ #

_results: list[tuple[str, bool, str]] = []  # (name, passed, detail)


def _test(name: str, passed: bool, detail: str = "") -> None:
    tag = "PASS" if passed else "FAIL"
    _results.append((name, passed, detail))
    line = f"  [{tag}] {name}"
    if detail:
        line += f"\n         {detail}"
    print(line)


def _section(title: str) -> None:
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


# ------------------------------------------------------------------ #
# Ensure inference.py is importable from the same directory
# ------------------------------------------------------------------ #

_ROOT = Path(__file__).parent
sys.path.insert(0, str(_ROOT))

try:
    from inference import (
        get_top4_recommendations,
        _PROPERTY_CATALOG,
        _PREPROCESSOR,
        _METADATA,
        _MODEL_WEIGHTS,
        _MODEL_CONFIG,
        _REQUIRED_PREF_KEYS,
        _FEATURE_COLUMNS,
    )
    _import_ok = True
except ImportError as e:
    print(f"[FAIL] Could not import inference.py: {e}")
    sys.exit(1)


# ================================================================== #
# TEST GROUP 1: Asset files exist
# ================================================================== #

_section("GROUP 1: Required asset files")

for path in (_PROPERTY_CATALOG, _PREPROCESSOR, _METADATA,
             _MODEL_WEIGHTS, _MODEL_CONFIG):
    _test(f"File present: {path.name}", path.exists(), str(path))


# ================================================================== #
# TEST GROUP 2: Input validation
# ================================================================== #

_section("GROUP 2: Input validation")

import traceback

VALID_PREFS = {
    "budget_max":           15_000_000,
    "min_area":             900,
    "max_area":             1_400,
    "bedroom_pref":         3,
    "bathroom_pref":        2,
    "balcony_pref":         1,
    "max_age":              10,
    "locality_pref":        "mira road",
    "city_pref":            "mumbai",
    "property_type_pref":   "apartment",
    "furnished_pref":       "semi-furnished",
}

# Missing required key
try:
    bad = {k: v for k, v in VALID_PREFS.items() if k != "budget_max"}
    get_top4_recommendations(bad)
    _test("Raises ValueError on missing key", False, "No exception raised")
except ValueError as e:
    _test("Raises ValueError on missing key", True, str(e)[:80])
except Exception as e:
    _test("Raises ValueError on missing key", False, f"Wrong exception: {e}")

# Negative numeric field
try:
    bad = dict(VALID_PREFS, budget_max=-1)
    get_top4_recommendations(bad)
    _test("Raises ValueError on negative budget_max", False)
except ValueError as e:
    _test("Raises ValueError on negative budget_max", True, str(e)[:80])
except Exception as e:
    _test("Raises ValueError on negative budget_max", False, f"Wrong: {e}")

# min_area > max_area
try:
    bad = dict(VALID_PREFS, min_area=2000, max_area=500)
    get_top4_recommendations(bad)
    _test("Raises ValueError when min_area > max_area", False)
except ValueError as e:
    _test("Raises ValueError when min_area > max_area", True, str(e)[:80])
except Exception as e:
    _test("Raises ValueError when min_area > max_area", False, f"Wrong: {e}")

# Non-numeric budget
try:
    bad = dict(VALID_PREFS, budget_max="not_a_number")
    get_top4_recommendations(bad)
    _test("Raises ValueError on non-numeric budget_max", False)
except ValueError as e:
    _test("Raises ValueError on non-numeric budget_max", True, str(e)[:80])
except Exception as e:
    _test("Raises ValueError on non-numeric budget_max", False, f"Wrong: {e}")

# Empty string category
try:
    bad = dict(VALID_PREFS, city_pref="")
    get_top4_recommendations(bad)
    _test("Raises ValueError on empty city_pref", False)
except ValueError as e:
    _test("Raises ValueError on empty city_pref", True, str(e)[:80])
except Exception as e:
    _test("Raises ValueError on empty city_pref", False, f"Wrong: {e}")

# zero budget_max
try:
    bad = dict(VALID_PREFS, budget_max=0)
    get_top4_recommendations(bad)
    _test("Raises ValueError on zero budget_max", False)
except ValueError as e:
    _test("Raises ValueError on zero budget_max", True, str(e)[:80])
except Exception as e:
    _test("Raises ValueError on zero budget_max", False, f"Wrong: {e}")


# ================================================================== #
# TEST GROUP 3: Core recommendation correctness
# (All tests below call the LIVE model with REAL assets)
# ================================================================== #

_section("GROUP 3: Core correctness — user profile #1 (Mira Road, 3BHK)")

# Profile #1 — user that was NOT part of the saved test-user rows
# (all saved test users are indexed U000001-U010000 with specific prefs;
#  this profile uses a combined preference not stored in any saved row)
profile_1 = {
    "budget_max":           15_000_000,
    "min_area":             900,
    "max_area":             1_400,
    "bedroom_pref":         3,
    "bathroom_pref":        2,
    "balcony_pref":         1,
    "max_age":              10,
    "locality_pref":        "mira road",
    "city_pref":            "mumbai",
    "property_type_pref":   "apartment",
    "furnished_pref":       "semi-furnished",
}

try:
    recs_1 = get_top4_recommendations(profile_1)
    _ok = True
except Exception as e:
    print(f"  [FAIL] get_top4_recommendations raised: {e}")
    traceback.print_exc()
    _ok = False
    recs_1 = []

_test("Returns a list", _ok and isinstance(recs_1, list))
_test("Returns exactly 4 results", _ok and len(recs_1) == 4,
      f"Got {len(recs_1)} results")

if _ok and recs_1:
    # All result dicts have required keys
    expected_keys = {
        "title", "price", "area", "bedroom_num", "bathroom_num",
        "balcony_num", "locality", "city", "property_type",
        "furnished", "age", "predicted_reward",
    }
    keys_ok = all(expected_keys.issubset(r.keys()) for r in recs_1)
    _test("All result dicts contain required keys", keys_ok,
          str(expected_keys - recs_1[0].keys()) if not keys_ok else "")

    # Scores are finite
    scores = [r["predicted_reward"] for r in recs_1]
    all_finite = all(math.isfinite(s) for s in scores)
    _test("All predicted_reward values are finite", all_finite,
          f"Scores: {scores}")

    # Scores in [0, 1]
    in_range = all(0.0 <= s <= 1.0 for s in scores)
    _test("All predicted_reward values in [0, 1]", in_range,
          f"Scores: {scores}")

    # Scores sorted descending
    sorted_desc = all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))
    _test("Scores sorted descending", sorted_desc,
          f"Scores: {[round(s, 4) for s in scores]}")

    # No duplicate titles
    titles = [r["title"] for r in recs_1]
    no_dups = len(titles) == len(set(titles))
    _test("No duplicate project titles", no_dups,
          f"Titles: {titles}" if not no_dups else "")

    # Results have non-empty strings for categorical fields
    cats_ok = all(
        isinstance(r["locality"], str) and r["locality"]
        and isinstance(r["city"], str) and r["city"]
        for r in recs_1
    )
    _test("Categorical fields are non-empty strings", cats_ok)

    # Print results for human inspection
    print()
    print("  Results (for manual inspection):")
    for i, r in enumerate(recs_1, 1):
        print(f"    #{i}: {r['title']!r}  "
              f"Rs.{r['price']:,.0f}  "
              f"{r['area']:.0f}sqft  "
              f"{r['bedroom_num']:.0f}BHK  "
              f"score={r['predicted_reward']:.4f}")


# ================================================================== #
# TEST GROUP 4: Second user profile — different preferences
# ================================================================== #

_section("GROUP 4: Core correctness — user profile #2 (Thane, 2BHK budget)")

profile_2 = {
    "budget_max":           8_000_000,
    "min_area":             500,
    "max_area":             900,
    "bedroom_pref":         2,
    "bathroom_pref":        2,
    "balcony_pref":         0,
    "max_age":              5,
    "locality_pref":        "thane",
    "city_pref":            "mumbai",
    "property_type_pref":   "apartment",
    "furnished_pref":       "unfurnished",
}

try:
    recs_2 = get_top4_recommendations(profile_2)
    _ok2 = True
except Exception as e:
    print(f"  [FAIL] get_top4_recommendations raised: {e}")
    traceback.print_exc()
    _ok2 = False
    recs_2 = []

_test("Returns list for profile #2", _ok2 and isinstance(recs_2, list))
_test("Returns exactly 4 for profile #2", _ok2 and len(recs_2) == 4,
      f"Got {len(recs_2)}")

if _ok2 and recs_2:
    scores_2 = [r["predicted_reward"] for r in recs_2]
    _test("Scores finite for profile #2",
          all(math.isfinite(s) for s in scores_2))
    _test("Scores descending for profile #2",
          all(scores_2[i] >= scores_2[i+1] for i in range(len(scores_2)-1)),
          f"Scores: {[round(s,4) for s in scores_2]}")
    titles_2 = [r["title"] for r in recs_2]
    _test("No duplicate titles for profile #2",
          len(titles_2) == len(set(titles_2)))

    # Profiles should return DIFFERENT top results
    if _ok and recs_1:
        titles_1 = [r["title"] for r in recs_1]
        different = titles_1 != titles_2
        _test("Profile #2 returns different results from profile #1",
              different, f"P1={titles_1}  P2={titles_2}")

    print()
    print("  Results:")
    for i, r in enumerate(recs_2, 1):
        print(f"    #{i}: {r['title']!r}  "
              f"Rs.{r['price']:,.0f}  "
              f"{r['area']:.0f}sqft  "
              f"score={r['predicted_reward']:.4f}")


# ================================================================== #
# TEST GROUP 5: Third user profile — low-budget studio / 1BHK
# ================================================================== #

_section("GROUP 5: Core correctness — user profile #3 (Kandivali, 1BHK)")

profile_3 = {
    "budget_max":           5_500_000,
    "min_area":             300,
    "max_area":             700,
    "bedroom_pref":         1,
    "bathroom_pref":        1,
    "balcony_pref":         0,
    "max_age":              15,
    "locality_pref":        "kandivali",
    "city_pref":            "mumbai",
    "property_type_pref":   "apartment",
    "furnished_pref":       "unfurnished",
}

try:
    recs_3 = get_top4_recommendations(profile_3)
    _ok3 = True
except Exception as e:
    print(f"  [FAIL] get_top4_recommendations raised: {e}")
    _ok3 = False
    recs_3 = []

_test("Returns list for profile #3", _ok3 and isinstance(recs_3, list))
_test("Returns 1-4 results for profile #3",
      _ok3 and 1 <= len(recs_3) <= 4,
      f"Got {len(recs_3)}")

if _ok3 and recs_3:
    scores_3 = [r["predicted_reward"] for r in recs_3]
    _test("Scores finite for profile #3",
          all(math.isfinite(s) for s in scores_3))
    _test("No duplicate titles for profile #3",
          len({r['title'] for r in recs_3}) == len(recs_3))

    print()
    print("  Results:")
    for i, r in enumerate(recs_3, 1):
        print(f"    #{i}: {r['title']!r}  Rs.{r['price']:,.0f}  score={r['predicted_reward']:.4f}")


# ================================================================== #
# TEST GROUP 6: Unknown category handling
# ================================================================== #

_section("GROUP 6: Unknown / unseen category values")

# An unknown locality_pref — the OHE's handle_unknown='ignore' should zero
# out that column and still return results
profile_unknown_locality = dict(
    VALID_PREFS,
    locality_pref="xyz_fictional_locality_not_in_training",
)

try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        recs_unk = get_top4_recommendations(profile_unknown_locality)
    _test("Returns results for unknown locality (handle_unknown=ignore)",
          isinstance(recs_unk, list) and len(recs_unk) > 0,
          f"Got {len(recs_unk)} results")
    if recs_unk:
        unk_scores = [r["predicted_reward"] for r in recs_unk]
        _test("Scores finite with unknown locality",
              all(math.isfinite(s) for s in unk_scores))
        print(f"  Results with unknown locality: {len(recs_unk)} returned")
except Exception as e:
    _test("Returns results for unknown locality", False, str(e)[:100])

# Case-insensitive input: "Mira Road" (title-case) should work like "mira road"
profile_mixed_case = dict(VALID_PREFS, locality_pref="Mira Road", city_pref="Mumbai")
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        recs_mc = get_top4_recommendations(profile_mixed_case)
    _test("Mixed-case input handled (normalised to lowercase)",
          isinstance(recs_mc, list) and len(recs_mc) == 4,
          f"Got {len(recs_mc)} results")
except Exception as e:
    _test("Mixed-case input handled", False, str(e)[:100])


# ================================================================== #
# TEST GROUP 7: Score ordering consistency across repeated calls
# ================================================================== #

_section("GROUP 7: Determinism — same input yields same output")

try:
    recs_a = get_top4_recommendations(profile_1)
    recs_b = get_top4_recommendations(profile_1)
    titles_match = [r["title"] for r in recs_a] == [r["title"] for r in recs_b]
    scores_match = [r["predicted_reward"] for r in recs_a] == \
                   [r["predicted_reward"] for r in recs_b]
    _test("Same preferences yield same titles on repeat call", titles_match)
    _test("Same preferences yield identical scores on repeat call", scores_match)
except Exception as e:
    _test("Determinism check", False, str(e)[:100])


# ================================================================== #
# TEST GROUP 8: Duplicate-project reporting
# ================================================================== #

_section("GROUP 8: Deduplication sanity")

# Verify that if the catalog has repeated project titles, only one appears
import pandas as pd

df_cat = pd.read_csv(_ROOT / "filtered_data.csv")
title_counts = df_cat["title"].value_counts()
multi_title_count = int((title_counts > 1).sum())
_test(
    f"Catalog contains {multi_title_count} project titles with >1 unit "
    "(deduplication is necessary)",
    multi_title_count > 0,
)

if _ok and recs_1:
    all_distinct = len({r["title"] for r in recs_1}) == len(recs_1)
    _test("Profile #1 top-4 contains no repeated project name", all_distinct)


# ================================================================== #
# FINAL SUMMARY
# ================================================================== #

print()
print("=" * 70)
print("  FINAL RESULTS")
print("=" * 70)

n_pass = sum(1 for _, p, _ in _results if p)
n_fail = sum(1 for _, p, _ in _results if not p)

print(f"\n  Tests run : {len(_results)}")
print(f"  Passed    : {n_pass}")
print(f"  Failed    : {n_fail}")

if n_fail:
    print("\n  FAILED TESTS:")
    for name, passed, detail in _results:
        if not passed:
            print(f"    - {name}")
            if detail:
                print(f"      {detail}")
    sys.exit(1)
else:
    print("\n  All tests passed.")
    sys.exit(0)
