
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import save_npz
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path("rl_interactions_v2.csv")
OUTPUT_DIR = Path("prepared_rl_data")
RANDOM_STATE = 42

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. LOAD AND VALIDATE DATA
# ============================================================

print("=" * 65)
print("REAL ESTATE RL DATA PREPARATION")
print("=" * 65)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Cannot find {INPUT_FILE}. "
        "Run this script from your RLRS project folder."
    )

df = pd.read_csv(INPUT_FILE)

required_columns = [
    "user_id", "property_id", "title", "reward",
    "price", "area", "price_per_sqft", "locality", "city",
    "property_type", "bedroom_num", "bathroom_num",
    "balcony_num", "furnished", "age",
    "budget_max", "min_area", "max_area",
    "bedroom_pref", "bathroom_pref", "balcony_pref",
    "locality_pref", "city_pref", "property_type_pref",
    "furnished_pref", "max_age"
]

missing_columns = sorted(set(required_columns) - set(df.columns))

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

if df[required_columns].isnull().any().any():
    raise ValueError(
        "Missing values detected. Clean the dataset before proceeding."
    )

if not df["reward"].between(0, 1).all():
    raise ValueError("Rewards must be between 0 and 1.")

if df["user_id"].nunique() < 10:
    raise ValueError("Not enough unique users for a reliable split.")

print(f"Rows loaded : {len(df):,}")
print(f"Unique users: {df['user_id'].nunique():,}")


# ============================================================
# 2. DEFINE MODEL INPUTS
# ============================================================

# Numerical property characteristics and user preferences
numeric_features = [
    "price",
    "area",
    "price_per_sqft",
    "bedroom_num",
    "bathroom_num",
    "balcony_num",
    "age",
    "budget_max",
    "min_area",
    "max_area",
    "bedroom_pref",
    "bathroom_pref",
    "balcony_pref",
    "max_age"
]

# Categorical property characteristics and user preferences
categorical_features = [
    "locality",
    "city",
    "property_type",
    "furnished",
    "locality_pref",
    "city_pref",
    "property_type_pref",
    "furnished_pref"
]

feature_columns = numeric_features + categorical_features

# Reward is the target, NOT an input.
# IDs and titles are excluded to avoid memorising records.
X = df[feature_columns].copy()
y = df["reward"].to_numpy(dtype=np.float32)
user_ids = df["user_id"].to_numpy()

# Standardise categorical text
for col in categorical_features:
    X[col] = (
        X[col]
        .astype(str)
        .str.strip()
        .str.lower()
        .replace("", "unknown")
    )

print(f"Numerical input features  : {len(numeric_features)}")
print(f"Categorical input features: {len(categorical_features)}")
print(f"Total input columns       : {len(feature_columns)}")


# ============================================================
# 3. SPLIT BY USER — NOT BY INDIVIDUAL ROW
# ============================================================

unique_users = np.sort(df["user_id"].unique())

train_users, temp_users = train_test_split(
    unique_users,
    test_size=0.20,
    random_state=RANDOM_STATE
)

val_users, test_users = train_test_split(
    temp_users,
    test_size=0.50,
    random_state=RANDOM_STATE
)

train_mask = np.isin(user_ids, train_users)
val_mask = np.isin(user_ids, val_users)
test_mask = np.isin(user_ids, test_users)

X_train = X.loc[train_mask]
X_val = X.loc[val_mask]
X_test = X.loc[test_mask]

y_train = y[train_mask]
y_val = y[val_mask]
y_test = y[test_mask]

print("\nUSER-LEVEL SPLIT")
print("-" * 65)
print(f"Training users   : {len(train_users):,}")
print(f"Validation users : {len(val_users):,}")
print(f"Testing users    : {len(test_users):,}")
print(f"Training rows    : {len(X_train):,}")
print(f"Validation rows  : {len(X_val):,}")
print(f"Testing rows     : {len(X_test):,}")


# ============================================================
# 4. PREPROCESS FEATURES
# ============================================================

# Fit preprocessing on training data only.
# Unseen categories in validation/test are handled safely.
try:
    encoder = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=True,
        dtype=np.float32
    )
except TypeError:
    # Compatibility with older scikit-learn versions
    encoder = OneHotEncoder(
        handle_unknown="ignore",
        sparse=True,
        dtype=np.float32
    )

preprocessor = ColumnTransformer(
    transformers=[
        ("numeric", StandardScaler(), numeric_features),
        ("categorical", encoder, categorical_features)
    ],
    remainder="drop",
    sparse_threshold=1.0
)

print("\nFitting preprocessing on training users...")

X_train_processed = preprocessor.fit_transform(X_train)
X_val_processed = preprocessor.transform(X_val)
X_test_processed = preprocessor.transform(X_test)

# Ensure all output matrices are sparse float32 matrices.
from scipy.sparse import csr_matrix

X_train_processed = csr_matrix(
    X_train_processed, dtype=np.float32
)
X_val_processed = csr_matrix(
    X_val_processed, dtype=np.float32
)
X_test_processed = csr_matrix(
    X_test_processed, dtype=np.float32
)

print("Feature preprocessing complete.")
print("Processed feature count:", X_train_processed.shape[1])


# ============================================================
# 5. SAVE PREPARED MATRICES AND TARGETS
# ============================================================

save_npz(OUTPUT_DIR / "X_train.npz", X_train_processed)
save_npz(OUTPUT_DIR / "X_val.npz", X_val_processed)
save_npz(OUTPUT_DIR / "X_test.npz", X_test_processed)

np.save(OUTPUT_DIR / "y_train.npy", y_train)
np.save(OUTPUT_DIR / "y_val.npy", y_val)
np.save(OUTPUT_DIR / "y_test.npy", y_test)

# Save preprocessing so future recommendations use
# precisely the same transformations.
joblib.dump(
    preprocessor,
    OUTPUT_DIR / "preprocessor.joblib"
)

# Save user IDs for evaluation and recommendation grouping.
pd.DataFrame({"user_id": train_users}).to_csv(
    OUTPUT_DIR / "train_users.csv", index=False
)
pd.DataFrame({"user_id": val_users}).to_csv(
    OUTPUT_DIR / "validation_users.csv", index=False
)
pd.DataFrame({"user_id": test_users}).to_csv(
    OUTPUT_DIR / "test_users.csv", index=False
)

# Save the actual user/property rows for ranking evaluation.
# These files retain the original reward and readable properties.
df.loc[train_mask].to_csv(
    OUTPUT_DIR / "train_reference.csv", index=False
)
df.loc[val_mask].to_csv(
    OUTPUT_DIR / "validation_reference.csv", index=False
)
df.loc[test_mask].to_csv(
    OUTPUT_DIR / "test_reference.csv", index=False
)

metadata = {
    "input_file": str(INPUT_FILE),
    "rows": int(len(df)),
    "unique_users": int(len(unique_users)),
    "train_users": int(len(train_users)),
    "validation_users": int(len(val_users)),
    "test_users": int(len(test_users)),
    "train_rows": int(len(X_train)),
    "validation_rows": int(len(X_val)),
    "test_rows": int(len(X_test)),
    "numeric_features": numeric_features,
    "categorical_features": categorical_features,
    "input_feature_count": int(X_train_processed.shape[1]),
    "target": "reward",
    "target_range": [0.0, 1.0],
    "split_method": "user-level, 80/10/10",
    "random_state": RANDOM_STATE
}

with open(OUTPUT_DIR / "metadata.json", "w") as f:
    json.dump(metadata, f, indent=4)

print("\n" + "=" * 65)
print("DATA PREPARATION COMPLETE")
print("=" * 65)
print(f"Processed features: {X_train_processed.shape[1]}")
print(f"Training matrix   : {X_train_processed.shape}")
print(f"Validation matrix : {X_val_processed.shape}")
print(f"Testing matrix    : {X_test_processed.shape}")
print(f"\nAll outputs saved in: {OUTPUT_DIR.resolve()}")
print("\nNo original CSV files were modified.")
print("Next step: build and train the RL value-estimation model.")
