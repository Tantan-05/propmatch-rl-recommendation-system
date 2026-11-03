"""
backend/main.py
===============
FastAPI backend for the Real Estate RL Recommendation System.

Imports and reuses get_top4_recommendations() from inference.py.
Does NOT duplicate recommendation logic.

Endpoints:
  GET  /api/health           — asset availability check
  POST /api/recommendations  — returns top-4 property recommendations
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator, model_validator

# ------------------------------------------------------------------ #
# Make project root importable so inference.py can be found
# ------------------------------------------------------------------ #

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from inference import (                          # noqa: E402
    get_top4_recommendations,
    _PROPERTY_CATALOG,
    _PREPROCESSOR,
    _MODEL_WEIGHTS,
    _MODEL_CONFIG,
)

# ------------------------------------------------------------------ #
# App setup
# ------------------------------------------------------------------ #

app = FastAPI(
    title="Real Estate RL Recommendation API",
    description=(
        "Returns top-4 property recommendations using a trained "
        "reward-prediction model. Scores reflect predicted suitability, "
        "not a purchase probability."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # frontend dev server + production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------ #
# Request schema — mirrors inference._REQUIRED_PREF_KEYS exactly
# ------------------------------------------------------------------ #

class PreferenceRequest(BaseModel):
    budget_max: float = Field(
        ..., gt=0, description="Maximum budget in INR"
    )
    min_area: float = Field(
        ..., ge=0, description="Minimum area in sq.ft"
    )
    max_area: float = Field(
        ..., ge=0, description="Maximum area in sq.ft"
    )
    bedroom_pref: float = Field(
        ..., ge=0, description="Preferred number of bedrooms"
    )
    bathroom_pref: float = Field(
        ..., ge=0, description="Preferred number of bathrooms"
    )
    balcony_pref: float = Field(
        ..., ge=0, description="Preferred number of balconies"
    )
    max_age: float = Field(
        ..., ge=0, description="Maximum acceptable property age in years"
    )
    locality_pref: str = Field(
        ..., min_length=1, description="Preferred locality (e.g. 'mira road')"
    )
    city_pref: str = Field(
        ..., min_length=1, description="Preferred city (e.g. 'mumbai')"
    )
    property_type_pref: str = Field(
        ..., min_length=1, description="e.g. 'apartment', 'villa'"
    )
    furnished_pref: str = Field(
        ..., min_length=1,
        description="'unfurnished', 'semi-furnished', or 'furnished'"
    )

    @field_validator("locality_pref", "city_pref", "property_type_pref",
                     "furnished_pref", mode="before")
    @classmethod
    def normalise_strings(cls, v: Any) -> str:
        if not isinstance(v, str) or not str(v).strip():
            raise ValueError("must be a non-empty string")
        return str(v).strip().lower()

    @model_validator(mode="after")
    def validate_area_range(self) -> "PreferenceRequest":
        if self.min_area > self.max_area:
            raise ValueError(
                f"min_area ({self.min_area}) must be <= max_area ({self.max_area})"
            )
        return self


# ------------------------------------------------------------------ #
# Response schema
# ------------------------------------------------------------------ #

class PropertyRecommendation(BaseModel):
    title: str
    price: float
    area: float
    bedroom_num: float
    bathroom_num: float
    balcony_num: float
    locality: str
    city: str
    property_type: str
    furnished: str
    age: float
    predicted_reward: float


class RecommendationResponse(BaseModel):
    recommendations: list[PropertyRecommendation]
    count: int


# ------------------------------------------------------------------ #
# Error handler
# ------------------------------------------------------------------ #

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


# ------------------------------------------------------------------ #
# GET /api/health
# ------------------------------------------------------------------ #

@app.get("/api/health", tags=["System"])
async def health_check() -> dict:
    """
    Check whether the backend is running and all required asset files exist.
    """
    assets = {
        "property_catalog":  _PROPERTY_CATALOG.exists(),
        "preprocessor":      _PREPROCESSOR.exists(),
        "model_weights":     _MODEL_WEIGHTS.exists(),
        "model_config":      _MODEL_CONFIG.exists(),
    }
    all_ok = all(assets.values())
    return {
        "status": "ok" if all_ok else "degraded",
        "assets": assets,
        "message": (
            "All assets available."
            if all_ok
            else "One or more required asset files are missing."
        ),
    }


# ------------------------------------------------------------------ #
# POST /api/recommendations
# ------------------------------------------------------------------ #

@app.post(
    "/api/recommendations",
    response_model=RecommendationResponse,
    tags=["Recommendations"],
)
async def get_recommendations(prefs: PreferenceRequest) -> RecommendationResponse:
    """
    Return up to 4 property recommendations for the given user preferences.

    The `predicted_reward` score (0–1) indicates how well each property
    matches the user's preferences according to the trained model.
    A higher score means a better predicted match — not a guarantee of
    satisfaction.
    """
    pref_dict = prefs.model_dump()

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            results = get_top4_recommendations(pref_dict, device="cpu")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    recs = [PropertyRecommendation(**r) for r in results]
    return RecommendationResponse(recommendations=recs, count=len(recs))
