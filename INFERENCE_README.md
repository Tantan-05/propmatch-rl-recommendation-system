# INFERENCE_README.md
# Real Estate RL + RS — Inference Module

## Overview

`inference.py` is a self-contained Python module that accepts a new user's
property preferences and returns the top-four distinct property
recommendations from the `filtered_data.csv` catalog.

It uses:
- **`prepared_rl_data/preprocessor.joblib`** — the fitted `ColumnTransformer`
  (StandardScaler + OneHotEncoder) from training. Called with `.transform()`
  only; never refitted.
- **`trained_rl_model/best_model.pth`** — the trained PyTorch reward-prediction
  model (497 → 256 → 128 → 64 → 1, Sigmoid output).
- **`filtered_data.csv`** — the full property catalog (60,255 listings).

The `predicted_reward` field in every result is a **suitability score in
[0, 1]** produced by the model. It is not a probability of purchase and does
not guarantee user satisfaction — it reflects how well a property matches the
user's stated preferences according to the synthetic reward function the model
was trained on.

---

## Required Input Fields

All eleven fields below are mandatory. Pass them as a Python dictionary.

| Field | Type | Meaning | Example |
|---|---|---|---|
| `budget_max` | `float` | Maximum budget in INR (must be > 0) | `15_000_000` |
| `min_area` | `float` | Minimum acceptable area in sq.ft | `900` |
| `max_area` | `float` | Maximum acceptable area in sq.ft (must be ≥ `min_area`) | `1_400` |
| `bedroom_pref` | `float` | Preferred number of bedrooms | `3` |
| `bathroom_pref` | `float` | Preferred number of bathrooms | `2` |
| `balcony_pref` | `float` | Preferred number of balconies | `1` |
| `max_age` | `float` | Maximum acceptable property age in years | `10` |
| `locality_pref` | `str` | Preferred locality (case-insensitive) | `"mira road"` |
| `city_pref` | `str` | Preferred city | `"mumbai"` |
| `property_type_pref` | `str` | Preferred property type | `"apartment"` |
| `furnished_pref` | `str` | Furnishing preference | `"semi-furnished"` |

### Supported categorical values (from training data)

**`city_pref`**: `"mumbai"`, `"western mumbai"`, `"central mumbai"`, `"mumbai south"`

**`property_type_pref`**: `"apartment"`, `"independent floor"`, `"independent house"`, `"villa"`

**`furnished_pref`**: `"unfurnished"`, `"semi-furnished"`, `"furnished"`

**`locality_pref`**: 172 localities seen during training. Top 10 by frequency:
`thane`, `mira road`, `kandivali`, `kharghar`, `dombivali`, `andheri`,
`panvel`, `chembur`, `badlapur`, `ulwe`.

> **Note:** An unrecognised `locality_pref` value will not raise an error. The
> OneHotEncoder was fitted with `handle_unknown='ignore'`, so the locality
> columns will be zeroed out and scoring will continue using the remaining
> features.

---

## Example Function Call

```python
from inference import get_top4_recommendations

prefs = {
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

results = get_top4_recommendations(prefs)

for rank, rec in enumerate(results, 1):
    print(f"#{rank}: {rec['title']}")
    print(f"  Price            : Rs. {rec['price']:,.0f}")
    print(f"  Area             : {rec['area']:,.0f} sq.ft")
    print(f"  BHK              : {rec['bedroom_num']:.0f}")
    print(f"  Locality         : {rec['locality']}")
    print(f"  Predicted reward : {rec['predicted_reward']:.4f}")
```

### Expected output

```
#1: Lodha New Launch
  Price            : Rs. 10,500,000
  Area             : 1,007 sq.ft
  BHK              : 3
  Locality         : mira road
  Predicted reward : 0.9978

#2: JP Codename StarLife
  Price            : Rs. 11,000,000
  Area             : 1,242 sq.ft
  BHK              : 3
  Locality         : mira road
  Predicted reward : 0.9888
...
```

---

## Output Format

`get_top4_recommendations()` returns a `list` of up to 4 `dict` objects,
sorted by `predicted_reward` descending. Each dict contains:

| Key | Type | Description |
|---|---|---|
| `title` | `str` | Project name (unique per result — deduplicated) |
| `price` | `float` | Listing price in INR |
| `area` | `float` | Area in sq.ft |
| `bedroom_num` | `float` | Number of bedrooms |
| `bathroom_num` | `float` | Number of bathrooms |
| `balcony_num` | `float` | Number of balconies |
| `locality` | `str` | Locality (lowercase) |
| `city` | `str` | City (lowercase) |
| `property_type` | `str` | Property type (lowercase) |
| `furnished` | `str` | Furnishing status (lowercase) |
| `age` | `float` | Property age in years |
| `predicted_reward` | `float` | Suitability score in [0, 1], 6 decimal places |

### Deduplication rule

When multiple units of the same project (same `title`) appear in the catalog,
only the unit with the **highest predicted suitability score** is returned.
This prevents showing "Dosti Eastern Bay x3" in the results.

---

## How to Run

### Demo (CLI)

```bash
# From the project root:
python inference.py
```

### As a module

```python
from inference import get_top4_recommendations
results = get_top4_recommendations({...})
```

### Test suite

```bash
python test_inference.py
```

The test suite:
- Loads the real preprocessor and model weights
- Runs 8 test groups (validation, 3 user profiles, unknown categories,
  case-insensitivity, determinism, deduplication)
- Reports PASS / FAIL for each check
- Exits with code 0 if all pass, 1 if any fail

---

## Known Limitations

1. **Scores measure synthetic-formula learning, not real user satisfaction.**
   The model was trained on synthetically generated rewards computed from a
   deterministic weighted formula. Metrics (R²=0.9986, NDCG@4=0.9994) reflect
   how well the model learned that formula on unseen users — not whether real
   users would prefer these properties.

2. **No feedback loop yet.** The system cannot update model weights based on
   which property a user selects. That component is planned for the next stage.

3. **Full catalog scan.** Every call to `get_top4_recommendations()` scores all
   60,255 properties. On CPU this takes roughly 2–5 seconds. For production,
   consider: (a) caching the catalog in memory between calls, or (b) adding a
   hard pre-filter (e.g. by city, max price) to reduce the candidate pool
   before running the model.

4. **sklearn version pinning.** The preprocessor was saved with scikit-learn
   1.7.1. A different version may raise `InconsistentVersionWarning`. Pin
   `scikit-learn==1.7.1` in your `requirements.txt` to avoid this.

5. **No guarantee of exactly 4 results.** If the entire catalog has fewer than
   4 distinct project titles (impossible with 9,247 unique titles), or if all
   candidates produce the same title, fewer than 4 results will be returned.
   The test suite checks for this edge case.

6. **No hard budget filter.** The model scores properties above the user's
   budget but penalises them via the learned reward function. Properties
   moderately above budget may still appear if no better matches exist. A hard
   `price <= budget_max` pre-filter can be added to `inference.py` if required.

---

## File Locations Required

All paths are resolved relative to `inference.py`'s location (the project root).

```
<project_root>/
    inference.py                          ← this module
    test_inference.py                     ← test suite
    filtered_data.csv                     ← property catalog
    prepared_rl_data/
        preprocessor.joblib               ← fitted ColumnTransformer
        metadata.json                     ← feature schema record
    trained_rl_model/
        best_model.pth                    ← trained model weights
        model_config.json                 ← architecture config
```

---

## Architecture Reference

```
Input (user prefs + property features)
    ↓
ColumnTransformer.transform()
    StandardScaler  → 14 numeric features
    OneHotEncoder   → 483 categorical features (305 locality + ... )
    Total           → 497 features
    ↓
PropertyValueNetwork (PyTorch, eval mode)
    Linear(497, 256) → ReLU → Dropout(0.1)
    Linear(256, 128) → ReLU → Dropout(0.1)
    Linear(128, 64)  → ReLU
    Linear(64, 1)    → Sigmoid
    ↓
predicted_reward ∈ [0, 1]
```
