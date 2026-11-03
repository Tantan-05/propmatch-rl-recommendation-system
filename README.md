# PropMatch — Real Estate RL Recommendation System

An AI-powered property recommendation web application built on a trained reinforcement-learning reward-prediction model. The model scores every listing in the property catalog against your stated preferences and returns the four best-matched properties.

> **Model note:** The `predicted_reward` score (0–1) reflects how well a property matches your preferences according to the trained model. It is a suitability score, not a purchase probability or market-value guarantee.

---

## Project structure

```
RLRS (1st training day - RS model)/
├── filtered_data.csv                  # Property catalog (60,255 listings)
├── prepared_rl_data/
│   ├── preprocessor.joblib            # Fitted ColumnTransformer (read-only)
│   └── metadata.json
├── trained_rl_model/
│   ├── best_model.pth                 # Trained PyTorch model (read-only)
│   └── model_config.json
│
├── inference.py                       # Core recommendation function
├── test_inference.py                  # 36 inference unit tests
│
├── backend/
│   └── main.py                        # FastAPI application
├── test_backend.py                    # Backend API tests (requires server running)
├── requirements.txt                   # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    # Root component
│   │   ├── main.jsx
│   │   ├── index.css                  # Design system
│   │   ├── api.js                     # Fetch wrappers
│   │   ├── constants.js               # Dropdown values
│   │   ├── utils.js                   # Formatting helpers
│   │   └── components/
│   │       ├── PreferenceForm.jsx
│   │       └── PropertyCard.jsx
│   ├── package.json
│   └── vite.config.js                 # Dev proxy → backend :8000
│
├── PROJECT_AUDIT.md
├── INFERENCE_README.md
└── README.md                          # This file
```

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10+ (tested 3.13.2) |
| Node.js | 18+ (tested 22.14.0) |
| npm | 8+ (tested 10.9.2) |

All Python packages (FastAPI, PyTorch, scikit-learn, etc.) are listed in `requirements.txt`.

---

## Installation

### 1. Python dependencies

```bash
# From the project root
pip install fastapi uvicorn[standard] pydantic httpx
# ML packages are expected to already be installed from model training.
# If not:
pip install -r requirements.txt
```

### 2. Frontend dependencies

```bash
cd frontend
npm install
```

---

## Starting the application

Open **two terminals** from the project root.

### Terminal 1 — Backend (FastAPI)

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 — Frontend (Vite dev server)

```bash
cd frontend
npm run dev
```

Expected output:
```
  VITE v5.x  ready in xxx ms
  ➜  Local:   http://localhost:5173/
```

Open **http://localhost:5173** in your browser.

> The Vite dev server proxies all `/api/*` requests to `http://localhost:8000` automatically — no manual CORS configuration needed.

---

## Running tests

### 1. Inference unit tests (no server required)

```bash
# From project root
python test_inference.py
```

Expected: `Tests run: 36  Passed: 36  Failed: 0`

### 2. Backend API tests (requires backend running on port 8000)

```bash
# Start backend first (Terminal 1 above), then:
python test_backend.py
```

Expected: `All backend tests passed.`

---

## API reference

### `GET /api/health`

Check whether the backend is running and all model assets are accessible.

**Response (200)**
```json
{
  "status": "ok",
  "assets": {
    "property_catalog": true,
    "preprocessor": true,
    "model_weights": true,
    "model_config": true
  },
  "message": "All assets available."
}
```

---

### `POST /api/recommendations`

Return up to four recommended properties ranked by predicted suitability.

**Request body**

```json
{
  "budget_max":          15000000,
  "min_area":            900,
  "max_area":            1400,
  "bedroom_pref":        3,
  "bathroom_pref":       2,
  "balcony_pref":        1,
  "max_age":             10,
  "locality_pref":       "mira road",
  "city_pref":           "mumbai",
  "property_type_pref":  "apartment",
  "furnished_pref":      "semi-furnished"
}
```

**Field reference**

| Field | Type | Constraint | Description |
|---|---|---|---|
| `budget_max` | float | > 0 | Maximum budget in INR |
| `min_area` | float | >= 0 | Minimum area in sq.ft |
| `max_area` | float | >= min_area | Maximum area in sq.ft |
| `bedroom_pref` | float | >= 0 | Preferred bedrooms |
| `bathroom_pref` | float | >= 0 | Preferred bathrooms |
| `balcony_pref` | float | >= 0 | Preferred balconies |
| `max_age` | float | >= 0 | Maximum property age (years) |
| `locality_pref` | string | non-empty | Preferred locality |
| `city_pref` | string | non-empty | Preferred city |
| `property_type_pref` | string | non-empty | e.g. `"apartment"`, `"villa"` |
| `furnished_pref` | string | non-empty | `"unfurnished"`, `"semi-furnished"`, `"furnished"` |

**Supported categorical values**

- **city_pref:** `mumbai`, `western mumbai`, `central mumbai`, `mumbai south`
- **property_type_pref:** `apartment`, `independent floor`, `independent house`, `villa`
- **furnished_pref:** `unfurnished`, `semi-furnished`, `furnished`
- **locality_pref:** 172 localities seen during training. Unknown values are handled gracefully (the OneHotEncoder zeros those columns).

**Response (200)**
```json
{
  "count": 4,
  "recommendations": [
    {
      "title": "Lodha New Launch",
      "price": 10500000,
      "area": 1007,
      "bedroom_num": 3,
      "bathroom_num": 2,
      "balcony_num": 1,
      "locality": "mira road",
      "city": "mumbai",
      "property_type": "apartment",
      "furnished": "semi-furnished",
      "age": 0,
      "predicted_reward": 0.997839
    }
  ]
}
```

**Error responses**

| Status | Condition |
|---|---|
| 422 | Missing field, invalid type, or constraint violation |
| 503 | Required model asset files not found |
| 500 | Unexpected model inference error |

---

## Building for production

```bash
cd frontend
npm run build
# Output goes to frontend/dist/
# Serve dist/ with any static file server, or integrate with FastAPI's StaticFiles
```

---

## Known limitations

1. **Scores reflect synthetic training data.** The model was trained on synthetically generated rewards. Real user satisfaction may differ. See `PROJECT_AUDIT.md` for a full analysis.

2. **Full catalog scan per request.** Every call scores all 60,255 properties. Typical response time is 2–5 seconds on CPU. For production, pre-filter by city or add caching.

3. **No hard budget filter.** Properties above `budget_max` may appear with lower scores. Add a hard filter in `inference.py` if strictly needed.

4. **No feedback loop.** The system cannot learn from user selections. This is planned as the next implementation phase.

5. **sklearn version.** The preprocessor was saved with scikit-learn 1.7.1. Pin this version to avoid `InconsistentVersionWarning`.
