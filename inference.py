"""
inference.py
============
Reusable inference module for the Real Estate RL + Recommendation System.

Usage
-----
    from inference import get_top4_recommendations

    prefs = {
        "budget_max":       15_000_000,
        "min_area":         900,
        "max_area":         1400,
        "bedroom_pref":     3,
        "bathroom_pref":    2,
        "balcony_pref":     1,
        "max_age":          10,
        "locality_pref":    "mira road",
        "city_pref":        "mumbai",
        "property_type_pref": "apartment",
        "furnished_pref":   "semi-furnished",
    }

    results = get_top4_recommendations(prefs)
    for r in results:
        print(r)

Notes
-----
- Uses the EXISTING fitted preprocessor (transform only, never refit).
- Uses the EXISTING trained model weights (eval mode, no gradients).
- All paths are resolved relative to this file's location.
- The 'predicted_reward' field is a suitability score in [0, 1] produced by
  the reward-prediction model. It is NOT a probability of purchase.
- Unknown categories (e.g. a locality not seen during training) are handled
  safely by the OneHotEncoder's handle_unknown='ignore' setting.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from scipy.sparse import csr_matrix

# ------------------------------------------------------------------ #
# Paths — all relative to this script's location
# ------------------------------------------------------------------ #

_ROOT = Path(__file__).parent
_PROPERTY_CATALOG  = _ROOT / "filtered_data.csv"
_PREPROCESSOR      = _ROOT / "prepared_rl_data" / "preprocessor.joblib"
_METADATA          = _ROOT / "prepared_rl_data" / "metadata.json"
_MODEL_WEIGHTS     = _ROOT / "trained_rl_model" / "best_model.pth"
_MODEL_CONFIG      = _ROOT / "trained_rl_model" / "model_config.json"

# ------------------------------------------------------------------ #
# Feature schema — mirrors prepare_rl_data.py exactly
# ------------------------------------------------------------------ #

_NUMERIC_FEATURES = [
    "price", "area", "price_per_sqft",
    "bedroom_num", "bathroom_num", "balcony_num", "age",
    "budget_max", "min_area", "max_area",
    "bedroom_pref", "bathroom_pref", "balcony_pref", "max_age",
]

_CATEGORICAL_FEATURES = [
    "locality", "city", "property_type", "furnished",
    "locality_pref", "city_pref", "property_type_pref", "furnished_pref",
]

_FEATURE_COLUMNS = _NUMERIC_FEATURES + _CATEGORICAL_FEATURES

# User preference fields (required in the input dict)
_REQUIRED_PREF_KEYS = [
    "budget_max", "min_area", "max_area",
    "bedroom_pref", "bathroom_pref", "balcony_pref", "max_age",
    "locality_pref", "city_pref", "property_type_pref", "furnished_pref",
]

# Property columns needed from filtered_data.csv
_PROPERTY_COLS = [
    "title", "price", "area", "price_per_sqft",
    "bedroom_num", "bathroom_num", "balcony_num",
    "furnished", "age", "locality", "city", "property_type",
]

# ------------------------------------------------------------------ #
# Neural network — identical to train_rl_model.ipynb
# ------------------------------------------------------------------ #

class _PropertyValueNetwork(nn.Module):
    def __init__(self, input_dim: int) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 256), nn.ReLU(), nn.Dropout(0.10),
            nn.Linear(256, 128),       nn.ReLU(), nn.Dropout(0.10),
            nn.Linear(128, 64),        nn.ReLU(),
            nn.Linear(64, 1),          nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x).squeeze(-1)


# ------------------------------------------------------------------ #
# Internal helpers
# ------------------------------------------------------------------ #

def _check_paths() -> None:
    """Raise a clear FileNotFoundError for any missing asset."""
    for path in (_PROPERTY_CATALOG, _PREPROCESSOR, _METADATA,
                 _MODEL_WEIGHTS, _MODEL_CONFIG):
        if not path.exists():
            raise FileNotFoundError(
                f"Required asset not found: {path}\n"
                "Run this module from the project root, or check that all "
                "prepared_rl_data/ and trained_rl_model/ files are present."
            )


def _validate_preferences(prefs: dict[str, Any]) -> dict[str, Any]:
    """
    Validate and coerce a user preferences dict.

    Returns a clean copy with all required keys present and numeric
    fields cast to the correct Python type.

    Raises
    ------
    ValueError  if a required key is missing or a value is invalid.
    """
    missing = [k for k in _REQUIRED_PREF_KEYS if k not in prefs]
    if missing:
        raise ValueError(
            f"Missing required preference keys: {missing}\n"
            f"Required keys are: {_REQUIRED_PREF_KEYS}"
        )

    clean: dict[str, Any] = {}

    # --- numeric preferences ---
    numeric_pref_keys = [
        "budget_max", "min_area", "max_area",
        "bedroom_pref", "bathroom_pref", "balcony_pref", "max_age",
    ]
    for key in numeric_pref_keys:
        try:
            val = float(prefs[key])
        except (TypeError, ValueError):
            raise ValueError(
                f"Preference '{key}' must be numeric; got {prefs[key]!r}"
            )
        if val < 0:
            raise ValueError(f"Preference '{key}' must be >= 0; got {val}")
        clean[key] = val

    if clean["min_area"] > clean["max_area"]:
        raise ValueError(
            f"min_area ({clean['min_area']}) must be <= max_area ({clean['max_area']})"
        )
    if clean["budget_max"] == 0:
        raise ValueError("budget_max must be > 0")

    # --- categorical preferences ---
    cat_pref_keys = [
        "locality_pref", "city_pref", "property_type_pref", "furnished_pref",
    ]
    for key in cat_pref_keys:
        val = prefs[key]
        if not isinstance(val, str) or not val.strip():
            raise ValueError(
                f"Preference '{key}' must be a non-empty string; got {val!r}"
            )
        clean[key] = str(val).strip().lower()

    return clean


def _load_property_catalog() -> pd.DataFrame:
    """
    Load filtered_data.csv and return only the columns needed for inference.

    Categorical columns are lowercased to match the training preprocessing
    applied in prepare_rl_data.py.
    """
    df = pd.read_csv(_PROPERTY_CATALOG, usecols=_PROPERTY_COLS)

    # Standardise categorical text exactly as in prepare_rl_data.py
    for col in ["locality", "city", "property_type", "furnished"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.lower()
            .replace("", "unknown")
        )

    # Drop rows missing any required field (none expected given audit results)
    required_non_null = [
        "price", "area", "price_per_sqft",
        "bedroom_num", "bathroom_num", "balcony_num",
        "age", "locality", "city", "property_type", "furnished",
    ]
    before = len(df)
    df = df.dropna(subset=required_non_null).reset_index(drop=True)
    after = len(df)
    if after < before:
        warnings.warn(
            f"{before - after} property rows dropped due to missing values.",
            RuntimeWarning,
            stacklevel=4,
        )

    return df


def _build_candidate_df(
    properties: pd.DataFrame,
    clean_prefs: dict[str, Any],
) -> pd.DataFrame:
    """
    Cross-join every property row with the user's preferences to form the
    22-column feature matrix expected by the preprocessor.
    """
    n = len(properties)

    candidate = properties.copy()

    # Attach user preference columns (broadcast scalar/string to all rows)
    for key in _REQUIRED_PREF_KEYS:
        candidate[key] = clean_prefs[key]

    # Standardise categorical preference columns (already lowercased in
    # _validate_preferences, but apply the same replace("","unknown") guard)
    for col in ["locality_pref", "city_pref", "property_type_pref", "furnished_pref"]:
        candidate[col] = (
            candidate[col]
            .astype(str)
            .str.strip()
            .str.lower()
            .replace("", "unknown")
        )

    return candidate


def _load_preprocessor():
    """Load the fitted ColumnTransformer from disk."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")   # suppress sklearn version warnings
        preprocessor = joblib.load(_PREPROCESSOR)
    return preprocessor


def _load_model(input_features: int, device: torch.device) -> _PropertyValueNetwork:
    """Reconstruct and load the trained model weights."""
    model = _PropertyValueNetwork(input_features).to(device)
    checkpoint = torch.load(
        _MODEL_WEIGHTS,
        map_location=device,
        weights_only=True,
    )
    model.load_state_dict(checkpoint)
    model.eval()
    return model


def _predict_rewards(
    candidate_df: pd.DataFrame,
    preprocessor,
    model: _PropertyValueNetwork,
    device: torch.device,
    batch_size: int = 2048,
) -> np.ndarray:
    """
    Transform candidate rows and run the model in batches.

    Returns a 1-D float32 array of predicted suitability scores, one per row.
    """
    X = candidate_df[_FEATURE_COLUMNS].copy()

    # Sparse CSR matrix — matches training pipeline
    X_processed = csr_matrix(
        preprocessor.transform(X),
        dtype=np.float32,
    )

    n_rows = X_processed.shape[0]
    scores: list[np.ndarray] = []

    with torch.no_grad():
        for start in range(0, n_rows, batch_size):
            end = min(start + batch_size, n_rows)
            batch = X_processed[start:end].toarray().astype(np.float32, copy=False)
            tensor = torch.from_numpy(batch).to(device)
            preds = model(tensor).cpu().numpy()
            scores.append(preds)

    return np.concatenate(scores)


def _deduplicate_by_title(
    df: pd.DataFrame,
    scores: np.ndarray,
    top_k: int = 4,
) -> list[dict[str, Any]]:
    """
    Rank all candidates by predicted score, then return up to top_k results
    keeping only one listing per project title (the highest-scoring unit).

    Returns a list of result dicts sorted by predicted_reward descending.
    """
    df = df.copy()
    df["predicted_reward"] = scores.astype(float)

    # Sort descending by score; use title + price as tiebreaker (stable)
    df = df.sort_values(
        ["predicted_reward", "price"],
        ascending=[False, True],
    )

    seen_titles: set[str] = set()
    results: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        title_key = str(row["title"]).strip()
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)

        results.append({
            "title":            title_key,
            "price":            float(row["price"]),
            "area":             float(row["area"]),
            "bedroom_num":      float(row["bedroom_num"]),
            "bathroom_num":     float(row["bathroom_num"]),
            "balcony_num":      float(row["balcony_num"]),
            "locality":         str(row["locality"]),
            "city":             str(row["city"]),
            "property_type":    str(row["property_type"]),
            "furnished":        str(row["furnished"]),
            "age":              float(row["age"]),
            "predicted_reward": round(float(row["predicted_reward"]), 6),
        })

        if len(results) == top_k:
            break

    return results


# ------------------------------------------------------------------ #
# Public API
# ------------------------------------------------------------------ #

def get_top4_recommendations(
    user_preferences: dict[str, Any],
    *,
    device: str = "cpu",
) -> list[dict[str, Any]]:
    """
    Return up to four distinct property recommendations for a new user.

    Parameters
    ----------
    user_preferences : dict
        Must contain all keys listed in _REQUIRED_PREF_KEYS:
            budget_max          (float)  maximum budget in INR
            min_area            (float)  minimum area in sq.ft
            max_area            (float)  maximum area in sq.ft
            bedroom_pref        (float)  preferred number of bedrooms
            bathroom_pref       (float)  preferred number of bathrooms
            balcony_pref        (float)  preferred number of balconies
            max_age             (float)  maximum acceptable property age (years)
            locality_pref       (str)    preferred locality (e.g. "mira road")
            city_pref           (str)    preferred city (e.g. "mumbai")
            property_type_pref  (str)    e.g. "apartment", "villa"
            furnished_pref      (str)    "unfurnished", "semi-furnished", "furnished"

    device : str
        PyTorch device string ("cpu" or "cuda"). Defaults to "cpu".

    Returns
    -------
    list[dict]
        Up to 4 dicts, each containing:
            title, price, area, bedroom_num, bathroom_num, balcony_num,
            locality, city, property_type, furnished, age, predicted_reward

        Sorted by predicted_reward descending.
        One entry per unique project title.

    Raises
    ------
    FileNotFoundError  if any required asset is missing.
    ValueError         if user_preferences is invalid.
    RuntimeError       if the model output fails the shape/sanity checks.
    """
    # 1. Asset existence check
    _check_paths()

    # 2. Validate and normalise preferences
    clean_prefs = _validate_preferences(user_preferences)

    # 3. Load assets
    with open(_MODEL_CONFIG) as f:
        model_cfg = json.load(f)

    torch_device = torch.device(device)
    preprocessor = _load_preprocessor()
    model        = _load_model(model_cfg["input_features"], torch_device)

    # 4. Load property catalog and build candidate matrix
    properties = _load_property_catalog()
    candidate_df = _build_candidate_df(properties, clean_prefs)

    # 5. Predict suitability scores
    scores = _predict_rewards(candidate_df, preprocessor, model, torch_device)

    # 6. Sanity checks
    if len(scores) != len(properties):
        raise RuntimeError(
            f"Score count ({len(scores)}) != property count ({len(properties)}). "
            "Preprocessing or model produced an unexpected output shape."
        )
    if not np.all(np.isfinite(scores)):
        n_bad = int(np.sum(~np.isfinite(scores)))
        raise RuntimeError(
            f"Model produced {n_bad} non-finite score(s). "
            "Check the model weights and input data."
        )
    if scores.min() < -1e-3 or scores.max() > 1 + 1e-3:
        warnings.warn(
            f"Scores outside expected [0, 1] range: "
            f"min={scores.min():.4f}, max={scores.max():.4f}",
            RuntimeWarning,
            stacklevel=2,
        )

    # 7. Rank and deduplicate
    return _deduplicate_by_title(candidate_df, scores, top_k=4)


# ------------------------------------------------------------------ #
# Quick CLI demo — python inference.py
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    example_prefs = {
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

    print("=" * 65)
    print("REAL ESTATE INFERENCE MODULE — DEMO")
    print("=" * 65)
    print("\nUser preferences:")
    for k, v in example_prefs.items():
        print(f"  {k}: {v}")
    print()

    recommendations = get_top4_recommendations(example_prefs)

    if not recommendations:
        print("No recommendations returned.")
    else:
        print(f"Top {len(recommendations)} recommendations:\n")
        for i, rec in enumerate(recommendations, 1):
            print(f"  Rank #{i}: {rec['title']}")
            print(f"    Price            : Rs. {rec['price']:,.0f}")
            print(f"    Area             : {rec['area']:,.0f} sq.ft")
            print(f"    BHK              : {rec['bedroom_num']:.0f}")
            print(f"    Locality         : {rec['locality']}")
            print(f"    Predicted reward : {rec['predicted_reward']:.4f}")
            print()
