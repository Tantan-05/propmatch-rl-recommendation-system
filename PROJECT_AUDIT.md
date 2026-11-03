# PROJECT AUDIT — Real Estate RL + Recommendation System

> **Audit date:** 2026-10-25  
> **Auditor:** Static code inspection + `audit_pipeline.py` execution  
> **Result:** All 11 check groups ran — zero FAIL, eight WARN, all pipeline checks PASS  
> **Files read:** `rl_environment_v2.py`, `prepare_rl_data.py`, `train_rl_model.ipynb`, `recommend_top4.ipynb`, all JSON configs, all CSV/NPZ/NPY artifacts  
> **Files modified:** None (read-only audit)

---

## 1. What Is Correctly Implemented

### 1.1 Data generation (`rl_environment_v2.py`)

| Item | Status |
|---|---|
| Reward is a deterministic weighted sum of 10 match-score components (budget, area, bedroom, bathroom, balcony, locality, city, property type, furnishing, age) | CORRECT |
| Reward computed after candidate selection — not used to filter candidates | CORRECT |
| Balanced candidate pool (20 strong / 15 moderate / 15 weak per user) creates a varied reward landscape | WELL-DESIGNED |
| `_candidate_score` helper column dropped before writing output; never appears in `rl_interactions_v2.csv` | CORRECT |
| 500,000 interactions across 10,000 users at 50 candidates each | CONFIRMED |

### 1.2 Data preparation (`prepare_rl_data.py`)

| Item | Status |
|---|---|
| `reward` excluded from input features (line 108 comment + actual code confirms) | CONFIRMED |
| `user_id`, `property_id`, `title` excluded to prevent ID memorisation | CONFIRMED |
| Split is user-level (splitting unique user IDs, not individual rows) | CONFIRMED |
| Preprocessor fitted only on training users, then applied unchanged to validation and test | CONFIRMED |
| Saved preprocessor matches the one used in inference (same `.joblib` file) | CONFIRMED |
| Metadata JSON records all feature names, counts and split sizes | COMPLETE |

### 1.3 Model training (`train_rl_model.ipynb`)

| Item | Status |
|---|---|
| Loads pre-split matrices from `prepared_rl_data/` — no re-splitting inside the notebook | CORRECT |
| Model checkpoint selected by validation RMSE, not test RMSE | CORRECT |
| Test data loaded after model selection (X_test not touched during training loop) | CONFIRMED |
| Early stopping with patience=5 triggered at epoch 20 | CONFIRMED |
| Architecture: 497 → 256 → 128 → 64 → 1 with ReLU + Sigmoid output | APPROPRIATE |
| Batch shuffling done by row index permutation (within training set only) | CORRECT |

### 1.4 Recommendation pipeline (`recommend_top4.ipynb`)

| Item | Status |
|---|---|
| Rankings by predicted reward, not actual reward (sort by `predicted_reward`) | CONFIRMED |
| `preprocessor.transform()` called — NOT `fit_transform()` — on test data | CORRECT |
| `ndcg_score([true_rewards], [predicted_scores], k=4)` — mathematically correct sklearn API call | CONFIRMED |
| `reward` column retained in output for audit purposes only, not used for ranking | CORRECT |

### 1.5 User-level split disjointness (executed check)

```
Train users : 8,000   Val users : 1,000   Test users : 1,000
Train+Val overlap  : 0
Train+Test overlap : 0
Val+Test overlap   : 0
Total unique       : 10,000
```

The three splits are fully disjoint. No user seen during training appears in validation or test.

---

## 2. Issues Confirmed from Code

### Issue 1 — Metrics measure synthetic-formula learning, not real generalisation

**Severity:** Conceptual — not a code bug, but critical to communicate clearly  
**Location:** `rl_environment_v2.py` (reward formula, lines 338–694); `train_rl_model.ipynb` (evaluation); `recommend_top4.ipynb` (NDCG)

The reward is a **deterministic weighted function** of the same 22 features that enter the model. There is zero stochastic noise in the reward signal. Given the input features, the reward value is always identical. The neural network is learning a known algebraic mapping.

- R² = 0.9986 means the model recovers the formula to within 0.14% unexplained variance. Expected for a noise-free target.
- NDCG@4 = 0.9994 means the model almost perfectly sorts 50 candidates by the formula. Also expected.
- Neither metric tells you how well the system serves real users whose true preferences differ from the simulated weights.

This is not a flaw in the pipeline — it is the nature of synthetic RL data. The pipeline is internally consistent. Metrics will change substantially once real user feedback is collected.

### Issue 2 — Duplicate property titles in candidate pools and top-4 output

**Severity:** UX concern — not a data leakage issue  
**Location:** `test_reference.csv`, `top4_recommendations.csv`

**Evidence from executed check:**
- 2,860 (user, title) pairs have the same property name appearing more than once within a single user's 50 candidates
- 379 users receive two or more identically-named properties within their top-4 recommendations
- Example: User U000004 receives "Dosti Eastern Bay" at ranks 2, 3, and 4 — same project name, different unit sizes and prices

**Why this happens:** `rl_environment_v2.py` deduplicates by `(title, price, area, locality)` combination (lines 1071–1078), allowing same project name with different unit specs through.

**Impact:** No leakage. Property IDs are unique. But a frontend showing "Dosti Eastern Bay" three times looks like a bug to users.

### Issue 3 — No reusable inference module for new users

**Severity:** Blocking for frontend development  
**Location:** `recommend_top4.ipynb` lines 183–189

The notebook loads `test_reference.csv`, a pre-merged file containing both user preferences and property rows, with the `reward` column already present. A new user visiting a frontend would have:
- Their preferences (budget, area, bedrooms, locality, etc.)
- No pre-stored candidate rows
- No `reward` column (it does not exist yet)

The existing code cannot serve a new user. All required components (preprocessor, model weights, property catalog) already exist — a wrapper script is simply missing.

### Issue 4 — Path mismatch between notebook and local filesystem

**Severity:** Minor — already resolved for HPC run; needs documenting for local use  
**Location:** `recommend_top4.ipynb` lines 186–187

```python
DATA_FILE         = BASE_DIR / "test_reference.csv"   # expects root
PREPROCESSOR_FILE = BASE_DIR / "preprocessor.joblib"  # expects root
```

Both files are actually in `prepared_rl_data/`. The notebook ran successfully on HPC because it was submitted from a directory where those files existed. Running locally from project root will raise `FileNotFoundError`.

---

## 3. Issues That Cannot Be Verified (Static Inspection Only)

| Item | Why not verifiable |
|---|---|
| Whether the scikit-learn version mismatch (1.7.1 vs 1.7.2) caused numerical differences in preprocessor output | Would require re-running both versions and comparing outputs byte-for-byte |
| Whether all 500,000 reward values in `rl_interactions_v2.csv` exactly match what `calculate_reward()` would produce today | Would require re-running `rl_environment_v2.py` (~hours); not appropriate for this audit |
| Whether the random seed makes HPC results exactly reproducible on a different machine | HPC shuffle states can differ between environments |
| Whether the 60,255 properties in `filtered_data.csv` are free of duplicate listings | Requires full dataset load; possible but out of scope |

---

## 4. Is the Existing Evaluation Trustworthy?

**Short answer: Yes, internally — but with an important ceiling.**

| Claim | Verdict |
|---|---|
| Pipeline has no data leakage | VERIFIED — TRUSTWORTHY |
| Preprocessing was correctly isolated to training data | VERIFIED — TRUSTWORTHY |
| Test users are genuinely unseen during training | VERIFIED — TRUSTWORTHY |
| NDCG computation is mathematically correct | VERIFIED — TRUSTWORTHY |
| R² = 0.9986 means good generalisation to new users | PARTIALLY TRUSTWORTHY — model generalises the synthetic formula, not real user behaviour |
| NDCG@4 = 0.9994 demonstrates a near-perfect recommendation system | MISLEADING AS HEADLINE — measures ranking accuracy against a known deterministic formula |

**The right framing:** The model has successfully learned to approximate a synthetic reward function on unseen users. This proves the pipeline is correctly implemented. It does not prove that real users will be satisfied with recommendations. Expect NDCG and R² to drop once real feedback is incorporated.

---

## 5. Prioritised Next-Step Plan

### Priority 1 — Build reusable inference module (BLOCKING)

Create `inference.py` with this contract:

```
Input : user preferences dict (budget_max, min_area, max_area, bedroom_pref,
        bathroom_pref, balcony_pref, max_age, locality_pref, city_pref,
        property_type_pref, furnished_pref)
Output: list of top-4 property dicts with predicted_reward and display fields

Steps:
  1. Load filtered_data.csv (property catalog)
  2. Apply optional hard filters (city, max_price, min_bedrooms)
  3. Cross-join user preferences with each candidate property row
  4. Apply preprocessor.transform() — never fit_transform()
  5. Run model in model.eval() mode with torch.no_grad()
  6. Sort by predicted_reward descending
  7. Deduplicate by project name (keep highest-scoring unit)
  8. Return top-4
```

This is the single most important engineering step.

### Priority 2 — Fix path mismatch in `recommend_top4.ipynb`

Update lines 186–187 to use `prepared_rl_data/`:
```python
DATA_FILE         = BASE_DIR / "prepared_rl_data" / "test_reference.csv"
PREPROCESSOR_FILE = BASE_DIR / "prepared_rl_data" / "preprocessor.joblib"
```

### Priority 3 — Add project-name deduplication

Before returning top-4, keep only the highest-predicted-reward unit per project name. This prevents showing "Dosti Eastern Bay" three times.

### Priority 4 — Define the feedback-collection schema

Before building the frontend, agree on:
- How a user "choice" event is recorded: `(user_id, session_id, shown_property_ids, chosen_property_id, timestamp)`
- Where feedback is stored: local SQLite, CSV, or database
- What format the feedback-learning update step expects

### Priority 5 — Implement feedback-based learning (after feedback schema)

See Section 6 for architecture details.

### Priority 6 — Frontend development

Only begin after priorities 1–4 are complete and `inference.py` is tested end-to-end.

---

## 6. Proposed Feedback-Learning Architecture

### Clearly stating what currently exists

The following do NOT exist in the current codebase:
- Real user clicks, selections or rejections
- Any "chosen property" signal
- A feedback-recording mechanism
- A model-update loop
- Simulated user choices (only synthetic reward values computed from a formula)

All 500,000 interactions are synthetically generated rewards. There is no user choice signal anywhere.

### Recommended approach: Fine-tuned Contextual Bandit

This builds directly on the existing model without replacing it.

#### Stage 1 — Collect real feedback (required before any learning)

When the frontend shows 4 properties:
```
Record: (user_preferences, [prop_1, prop_2, prop_3, prop_4], chosen_index)
chosen_index: 0-3 = selected that property | -1 = no selection
```
Store as rows in `user_feedback.csv` or a database table.

#### Stage 2 — Convert feedback to training signal

Use the contextual bandit formulation:

```
Context  : user preferences (same 11 columns as current input)
Action   : the property shown at each position
Reward   : 1.0 if user selected this property, 0.0 if shown but not chosen
```

This is bandit feedback — you only observe reward for shown actions. Properties never displayed in a session receive no update (avoids counterfactual bias).

#### Stage 3 — Update the model (two options)

**Option A — Direct fine-tuning (simpler):**
```python
# Per feedback session:
x_chosen   = preprocess(user_prefs + chosen_property)   # label = 1.0
x_rejected = [preprocess(user_prefs + p)               # label = 0.0
              for p in shown_but_unchosen]
loss = mse_loss(model(x_all), labels)
loss.backward()
optimizer.step()   # small lr = 1e-4 to avoid catastrophic forgetting
```

**Option B — Periodic batch fine-tuning (recommended):**
1. Accumulate feedback for N sessions (e.g., N=100)
2. Combine with a random sample of original training data (prevents forgetting)
3. Run 1–3 epochs of fine-tuning
4. Evaluate on a held-out feedback set before swapping the model

#### Stage 4 — Exploration strategy (prevents learning collapse)

Without exploration the system only shows high-confidence properties and never discovers user preferences for less-seen properties.

Options:
- **Epsilon-greedy:** With probability 0.10, replace one of top-4 with a random property
- **Thompson Sampling:** Add Gaussian noise to predicted rewards before ranking (preserves relative ordering better)

#### What reuses your existing system

| Component | Reused As-Is |
|---|---|
| `preprocessor.joblib` | Same preprocessing for real user preferences |
| `best_model.pth` | Warm-start point — not discarded |
| `PropertyValueNetwork` architecture | Unchanged |
| `filtered_data.csv` property catalog | Candidate source |
| 22 feature columns | Same |

#### What is new

| Component | Notes |
|---|---|
| `inference.py` | Takes raw user prefs, returns top-4 |
| Feedback storage | `user_feedback.csv` or SQLite |
| `update_model.py` | Reads feedback, runs gradient updates |
| Exploration flag | Epsilon-greedy or noise injection in inference |

---

## 7. Frontend Readiness Checklist

All items below must be satisfied before frontend development begins.

- [ ] `inference.py` exists and is tested end-to-end with a sample user preferences dict
- [ ] `inference.py` returns top-4 property dicts without requiring a pre-stored interaction row
- [ ] Path mismatch fixed in `recommend_top4.ipynb`
- [ ] Project-name deduplication implemented in inference module
- [ ] `inference.py` handles cold-start new users
- [ ] `inference.py` handles unseen category values gracefully (verify `handle_unknown='ignore'` works)
- [ ] Candidate pool strategy decided (full 60,255 properties or pre-filtered subset)
- [ ] Model serving environment decided (Python script, FastAPI, or other)
- [ ] sklearn version pinned to 1.7.1 in `requirements.txt`
- [ ] Feedback schema defined and documented (even if not yet implemented)

---

## Appendix — Audit Script Results

`audit_pipeline.py` was executed in the project root. All 11 check groups completed successfully.

| Check | Result |
|---|---|
| All required files present | PASS |
| User-level split fully disjoint | PASS (0 overlaps across all pairs) |
| Reward excluded from input features | PASS |
| Preprocessor fitted on training only | PASS |
| Target values in [0, 1] | PASS |
| Model config consistent with artifacts | PASS |
| Ranking uses predicted not actual rewards | PASS |
| NDCG formula correct | PASS |
| NDCG@4 extremely high (formula learning) | WARN |
| Duplicate property titles present | WARN (UX, not leakage) |
| New-user inference module missing | WARN (blocking) |
| Feedback learning not implemented | WARN (expected at this stage) |

**Zero FAIL results. The pipeline is internally sound.**
