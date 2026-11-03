"""
test_backend.py
===============
Backend API tests for the FastAPI recommendation service.

Requires the backend to be RUNNING on http://localhost:8000 before executing.

Run:
    # Terminal 1 — start backend
    cd backend
    uvicorn main:app --host 0.0.0.0 --port 8000

    # Terminal 2 — run tests
    python test_backend.py
"""

from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
from typing import Any

BASE_URL = "http://localhost:8000"

# ------------------------------------------------------------------ #
# Minimal HTTP helpers (stdlib only — no httpx/requests required)
# ------------------------------------------------------------------ #

def get(path: str) -> tuple[int, Any]:
    url = BASE_URL + path
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as e:
        print(f"  Connection error: {e}")
        print("  Is the backend running?  →  cd backend && uvicorn main:app --port 8000")
        sys.exit(1)


def post(path: str, payload: dict) -> tuple[int, Any]:
    url = BASE_URL + path
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as e:
        print(f"  Connection error: {e}")
        print("  Is the backend running?  →  cd backend && uvicorn main:app --port 8000")
        sys.exit(1)


# ------------------------------------------------------------------ #
# Test framework
# ------------------------------------------------------------------ #

_results: list[tuple[str, bool, str]] = []

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
# Valid preference payload (new profile — not from test_inference.py)
# ------------------------------------------------------------------ #

VALID_PREFS = {
    "budget_max":          20_000_000,
    "min_area":            1100,
    "max_area":            1800,
    "bedroom_pref":        3,
    "bathroom_pref":       3,
    "balcony_pref":        2,
    "max_age":             8,
    "locality_pref":       "andheri",
    "city_pref":           "mumbai",
    "property_type_pref":  "apartment",
    "furnished_pref":      "semi-furnished",
}


# ================================================================== #
# TEST: GET /api/health
# ================================================================== #

_section("GET /api/health")

status, body = get("/api/health")
_test("HTTP 200 returned", status == 200, f"Got {status}")
_test("'status' field present", "status" in body)
_test("'assets' field present", "assets" in body)
_test("All assets available", body.get("status") == "ok",
      str(body.get("assets", {})))
print(f"  Health message: {body.get('message', '—')}")


# ================================================================== #
# TEST: POST /api/recommendations — valid input
# ================================================================== #

_section("POST /api/recommendations — valid profile (Andheri, 3BHK)")

status, body = post("/api/recommendations", VALID_PREFS)
_test("HTTP 200 returned", status == 200, f"Got {status}")
_test("'recommendations' key present", "recommendations" in body)
_test("'count' key present", "count" in body)

recs = body.get("recommendations", [])
_test("Exactly 4 recommendations returned", len(recs) == 4, f"Got {len(recs)}")

if recs:
    expected_keys = {
        "title", "price", "area", "bedroom_num", "bathroom_num",
        "balcony_num", "locality", "city", "property_type",
        "furnished", "age", "predicted_reward",
    }
    keys_ok = all(expected_keys.issubset(r.keys()) for r in recs)
    _test("All result dicts contain required keys", keys_ok)

    scores = [r["predicted_reward"] for r in recs]
    _test("Scores are floats in [0, 1]",
          all(isinstance(s, (int, float)) and 0 <= s <= 1 for s in scores),
          f"Scores: {scores}")
    _test("Scores sorted descending",
          all(scores[i] >= scores[i+1] for i in range(len(scores)-1)),
          f"Scores: {[round(s,4) for s in scores]}")

    titles = [r["title"] for r in recs]
    _test("No duplicate project titles", len(titles) == len(set(titles)),
          f"Titles: {titles}")

    print()
    print("  Results (verified against real model):")
    for i, r in enumerate(recs, 1):
        print(f"    #{i}: {r['title']!r}  Rs.{r['price']:,.0f}  score={r['predicted_reward']:.4f}")


# ================================================================== #
# TEST: POST /api/recommendations — second profile not in test suite
# ================================================================== #

_section("POST /api/recommendations — new profile (Powai, 2BHK luxury)")

luxury_prefs = {
    "budget_max":          40_000_000,
    "min_area":            1500,
    "max_area":            3000,
    "bedroom_pref":        3,
    "bathroom_pref":       3,
    "balcony_pref":        2,
    "max_age":             5,
    "locality_pref":       "powai",
    "city_pref":           "mumbai",
    "property_type_pref":  "apartment",
    "furnished_pref":      "furnished",
}

status2, body2 = post("/api/recommendations", luxury_prefs)
_test("HTTP 200 returned", status2 == 200, f"Got {status2}")
recs2 = body2.get("recommendations", [])
_test("Returns 1-4 results", 1 <= len(recs2) <= 4, f"Got {len(recs2)}")
if recs2:
    scores2 = [r["predicted_reward"] for r in recs2]
    _test("Scores finite and in [0,1]", all(0<=s<=1 for s in scores2))
    _test("Titles distinct", len({r["title"] for r in recs2}) == len(recs2))
    # Results must differ from first profile
    if recs:
        same = [r["title"] for r in recs] == [r["title"] for r in recs2]
        _test("Different profile yields different results", not same)
    print()
    print("  Results:")
    for i, r in enumerate(recs2, 1):
        print(f"    #{i}: {r['title']!r}  Rs.{r['price']:,.0f}  score={r['predicted_reward']:.4f}")


# ================================================================== #
# TEST: Invalid inputs
# ================================================================== #

_section("POST /api/recommendations - invalid inputs")

# Missing required field
status_m, body_m = post("/api/recommendations",
    {k: v for k, v in VALID_PREFS.items() if k != "budget_max"})
_test("Missing field -> 422", status_m == 422, f"Got {status_m}: {body_m}")

# Negative budget
status_n, body_n = post("/api/recommendations", dict(VALID_PREFS, budget_max=-1))
_test("Negative budget_max -> 422", status_n == 422, f"Got {status_n}")

# min_area > max_area
status_a, body_a = post("/api/recommendations",
    dict(VALID_PREFS, min_area=2000, max_area=500))
_test("min_area > max_area -> 422", status_a == 422, f"Got {status_a}")

# Empty string city
status_e, body_e = post("/api/recommendations", dict(VALID_PREFS, city_pref=""))
_test("Empty city_pref -> 422", status_e == 422, f"Got {status_e}")

# Zero budget
status_z, body_z = post("/api/recommendations", dict(VALID_PREFS, budget_max=0))
_test("Zero budget_max -> 422", status_z == 422, f"Got {status_z}")


# ================================================================== #
# TEST: Unknown category passes through (handle_unknown='ignore')
# ================================================================== #

_section("POST /api/recommendations — unknown locality (OHE ignore)")

status_u, body_u = post("/api/recommendations",
    dict(VALID_PREFS, locality_pref="xyz_fictional_locality_not_in_training"))
_test("Unknown locality still returns HTTP 200", status_u == 200, f"Got {status_u}")
recs_u = body_u.get("recommendations", [])
_test("Returns results despite unknown locality",
      isinstance(recs_u, list) and len(recs_u) > 0, f"Got {len(recs_u)}")


# ================================================================== #
# SUMMARY
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
            print(f"    - {name}: {detail}")
    sys.exit(1)
else:
    print("\n  All backend tests passed.")
    sys.exit(0)
