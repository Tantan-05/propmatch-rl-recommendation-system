import pandas as pd
import numpy as np
import json
import os

# ============================================================
# REAL-ESTATE RL ENVIRONMENT / CANDIDATE + REWARD GENERATOR
# ============================================================
#
# INPUT:
#   filtered_data.csv       -> property dataset
#   simulated_users.csv     -> simulated user preferences
#
# OUTPUT:
#   rl_interactions.csv     -> user-property interactions + rewards
#   rl_environment_config.json
#
# PURPOSE:
#   1. Generate candidate properties for each user.
#   2. Calculate how well each property matches the user.
#   3. Produce a reward value for every user-property interaction.
#
# This file DOES NOT train the RL model yet.
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

PROPERTY_FILE = "filtered_data.csv"
USER_FILE = "simulated_users.csv"

OUTPUT_INTERACTIONS = "rl_interactions.csv"
OUTPUT_CONFIG = "rl_environment_config.json"

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# Number of candidate properties considered per user.
# We deliberately avoid comparing every user with all 60k properties.
CANDIDATES_PER_USER = 50


# ============================================================
# 1. LOAD DATA
# ============================================================

print("=" * 75)
print("REAL-ESTATE RL ENVIRONMENT")
print("=" * 75)

print("\n[1/8] Loading datasets...")

properties = pd.read_csv(PROPERTY_FILE)
users = pd.read_csv(USER_FILE)

print(f"Properties loaded : {len(properties):,}")
print(f"Users loaded      : {len(users):,}")


# ============================================================
# 2. VALIDATE PROPERTY DATA
# ============================================================

print("\n[2/8] Validating property dataset...")

required_property_columns = [
    "title",
    "price",
    "area",
    "price_per_sqft",
    "locality",
    "city",
    "property_type",
    "bedroom_num",
    "bathroom_num",
    "balcony_num",
    "furnished",
    "age"
]

missing_property_columns = [
    c for c in required_property_columns
    if c not in properties.columns
]

if missing_property_columns:
    raise ValueError(
        "Missing property columns:\n"
        + str(missing_property_columns)
    )


# ============================================================
# 3. VALIDATE USER DATA
# ============================================================

print("[3/8] Validating simulated-user dataset...")

required_user_columns = [
    "user_id",
    "budget_max",
    "min_area",
    "max_area",
    "bedroom_pref",
    "bathroom_pref",
    "balcony_pref",
    "locality_pref",
    "city_pref",
    "property_type_pref",
    "furnished_pref",
    "max_age"
]

missing_user_columns = [
    c for c in required_user_columns
    if c not in users.columns
]

if missing_user_columns:
    raise ValueError(
        "Missing user columns:\n"
        + str(missing_user_columns)
    )


# ============================================================
# 4. CLEAN / STANDARDIZE VALUES
# ============================================================

print("\n[4/8] Cleaning and standardizing values...")


# -----------------------------
# Numeric property columns
# -----------------------------

property_numeric = [
    "price",
    "area",
    "price_per_sqft",
    "bedroom_num",
    "bathroom_num",
    "balcony_num",
    "age"
]

for col in property_numeric:
    properties[col] = pd.to_numeric(
        properties[col],
        errors="coerce"
    )


# -----------------------------
# Categorical property columns
# -----------------------------

property_categorical = [
    "locality",
    "city",
    "property_type",
    "furnished"
]

for col in property_categorical:
    properties[col] = (
        properties[col]
        .astype(str)
        .str.strip()
        .str.lower()
    )


# -----------------------------
# Numeric user columns
# -----------------------------

user_numeric = [
    "budget_max",
    "min_area",
    "max_area",
    "bedroom_pref",
    "bathroom_pref",
    "balcony_pref",
    "max_age"
]

for col in user_numeric:
    users[col] = pd.to_numeric(
        users[col],
        errors="coerce"
    )


# -----------------------------
# Categorical user columns
# -----------------------------

user_categorical = [
    "locality_pref",
    "city_pref",
    "property_type_pref",
    "furnished_pref"
]

for col in user_categorical:
    users[col] = (
        users[col]
        .astype(str)
        .str.strip()
        .str.lower()
    )


# -----------------------------
# Remove unusable properties
# -----------------------------

properties = properties.dropna(
    subset=[
        "price",
        "area",
        "bedroom_num",
        "bathroom_num",
        "balcony_num",
        "age",
        "locality",
        "city",
        "property_type",
        "furnished"
    ]
).copy()


# -----------------------------
# Remove unusable users
# -----------------------------

users = users.dropna(
    subset=required_user_columns
).copy()


properties.reset_index(drop=True, inplace=True)
users.reset_index(drop=True, inplace=True)


print(f"Usable properties : {len(properties):,}")
print(f"Usable users      : {len(users):,}")


# ============================================================
# 5. REWARD FUNCTION
# ============================================================
#
# The reward represents:
#
# "How suitable is this property for this user?"
#
# Maximum reward = 1.0
# Minimum reward = 0.0
#
# We use weighted components because not every preference
# has equal importance.
#
# IMPORTANT:
# This reward is NOT the final RL algorithm.
#
# It defines the feedback signal that the RL agent will learn
# to maximize.
# ============================================================

print("\n[5/8] Setting up reward function...")


def calculate_reward(user, property_row):
    """
    Calculate normalized suitability reward
    for one user-property pair.

    Reward range:
        0.0 = very poor match
        1.0 = excellent match
    """

    scores = {}

    # --------------------------------------------------------
    # 1. BUDGET
    # --------------------------------------------------------

    price = float(property_row["price"])
    budget = float(user["budget_max"])

    if price <= budget:
        budget_score = 1.0

    else:
        # Gradually penalize properties over budget.
        overshoot = (price - budget) / budget

        budget_score = max(
            0.0,
            1.0 - (overshoot * 2.0)
        )

    scores["budget"] = budget_score


    # --------------------------------------------------------
    # 2. AREA
    # --------------------------------------------------------

    area = float(property_row["area"])
    min_area = float(user["min_area"])
    max_area = float(user["max_area"])

    if min_area <= area <= max_area:

        area_score = 1.0

    elif area < min_area:

        difference = (min_area - area) / min_area

        area_score = max(
            0.0,
            1.0 - difference
        )

    else:

        difference = (area - max_area) / max_area

        area_score = max(
            0.0,
            1.0 - difference
        )

    scores["area"] = area_score


    # --------------------------------------------------------
    # 3. BEDROOM
    # --------------------------------------------------------

    bedroom = float(property_row["bedroom_num"])
    bedroom_pref = float(user["bedroom_pref"])

    if bedroom == bedroom_pref:
        bedroom_score = 1.0
    else:
        bedroom_score = max(
            0.0,
            1.0 - abs(bedroom - bedroom_pref) * 0.5
        )

    scores["bedroom"] = bedroom_score


    # --------------------------------------------------------
    # 4. BATHROOM
    # --------------------------------------------------------

    bathroom = float(property_row["bathroom_num"])
    bathroom_pref = float(user["bathroom_pref"])

    if bathroom >= bathroom_pref:
        bathroom_score = 1.0
    else:
        difference = bathroom_pref - bathroom

        bathroom_score = max(
            0.0,
            1.0 - difference * 0.5
        )

    scores["bathroom"] = bathroom_score


    # --------------------------------------------------------
    # 5. BALCONY
    # --------------------------------------------------------

    balcony = float(property_row["balcony_num"])
    balcony_pref = float(user["balcony_pref"])

    if balcony >= balcony_pref:
        balcony_score = 1.0
    else:
        difference = balcony_pref - balcony

        balcony_score = max(
            0.0,
            1.0 - difference * 0.4
        )

    scores["balcony"] = balcony_score


    # --------------------------------------------------------
    # 6. LOCALITY
    # --------------------------------------------------------

    property_locality = str(property_row["locality"])
    user_locality = str(user["locality_pref"])

    if property_locality == user_locality:
        locality_score = 1.0
    else:
        locality_score = 0.0

    scores["locality"] = locality_score


    # --------------------------------------------------------
    # 7. CITY
    # --------------------------------------------------------

    property_city = str(property_row["city"])
    user_city = str(user["city_pref"])

    if property_city == user_city:
        city_score = 1.0
    else:
        city_score = 0.0

    scores["city"] = city_score


    # --------------------------------------------------------
    # 8. PROPERTY TYPE
    # --------------------------------------------------------

    property_type = str(property_row["property_type"])
    user_property_type = str(user["property_type_pref"])

    if property_type == user_property_type:
        property_type_score = 1.0
    else:
        property_type_score = 0.0

    scores["property_type"] = property_type_score


    # --------------------------------------------------------
    # 9. FURNISHING
    # --------------------------------------------------------

    furnished = str(property_row["furnished"])
    user_furnished = str(user["furnished_pref"])

    if furnished == user_furnished:
        furnished_score = 1.0
    else:
        furnished_score = 0.0

    scores["furnished"] = furnished_score


    # --------------------------------------------------------
    # 10. PROPERTY AGE
    # --------------------------------------------------------

    age = float(property_row["age"])
    max_age = float(user["max_age"])

    if age <= max_age:
        age_score = 1.0
    else:

        excess_age = (age - max_age) / max_age

        age_score = max(
            0.0,
            1.0 - excess_age
        )

    scores["age"] = age_score


    # ========================================================
    # WEIGHTS
    # ========================================================
    #
    # The weights represent the importance of each factor.
    #
    # Price + location + BHK are intentionally stronger
    # because they are generally more important in property
    # selection.
    # ========================================================

    weights = {

        "budget": 0.20,

        "area": 0.12,

        "bedroom": 0.15,

        "bathroom": 0.08,

        "balcony": 0.04,

        "locality": 0.15,

        "city": 0.08,

        "property_type": 0.07,

        "furnished": 0.06,

        "age": 0.05
    }


    # --------------------------------------------------------
    # FINAL WEIGHTED REWARD
    # --------------------------------------------------------

    reward = sum(
        scores[key] * weights[key]
        for key in weights
    )

    return float(np.clip(reward, 0.0, 1.0))


# ============================================================
# 6. CANDIDATE GENERATION
# ============================================================
#
# We don't want:
#
# 10,000 users × 60,000 properties
#
# = 600 million interactions.
#
# Instead, we retrieve a manageable candidate pool.
#
# Candidate retrieval uses broad preferences first.
#
# The RL agent will later rank these candidates.
# ============================================================

print("\n[6/8] Generating candidate properties...")


def get_candidates(user, properties, n_candidates=50):

    candidate_df = properties.copy()

    # --------------------------------------------------------
    # STEP A: Prefer same city
    # --------------------------------------------------------

    city_matches = candidate_df[
        candidate_df["city"] == user["city_pref"]
    ]

    if len(city_matches) >= n_candidates:

        candidate_df = city_matches

    elif len(city_matches) > 0:

        candidate_df = city_matches


    # --------------------------------------------------------
    # STEP B: Prefer properties within/near budget
    # --------------------------------------------------------

    budget_limit = user["budget_max"]

    within_budget = candidate_df[
        candidate_df["price"] <= budget_limit
    ]

    if len(within_budget) >= n_candidates:

        candidate_df = within_budget

    elif len(within_budget) > 0:

        candidate_df = within_budget


    # --------------------------------------------------------
    # STEP C: Prefer matching bedroom count
    # --------------------------------------------------------

    bedroom_matches = candidate_df[
        candidate_df["bedroom_num"]
        == user["bedroom_pref"]
    ]

    if len(bedroom_matches) >= n_candidates:

        candidate_df = bedroom_matches

    elif len(bedroom_matches) > 0:

        candidate_df = bedroom_matches


    # --------------------------------------------------------
    # STEP D: If enough candidates exist,
    # randomly sample them.
    #
    # Otherwise use all available candidates.
    # --------------------------------------------------------

    if len(candidate_df) > n_candidates:

        candidate_df = candidate_df.sample(
            n=n_candidates,
            random_state=np.random.randint(0, 1_000_000)
        )

    else:

        candidate_df = candidate_df.copy()


    # --------------------------------------------------------
    # If the filtering became too restrictive and produced
    # very few properties, supplement candidates from the
    # original property dataset.
    # --------------------------------------------------------

    if len(candidate_df) < min(10, n_candidates):

        fallback = properties.sample(
            n=min(
                n_candidates,
                len(properties)
            ),
            random_state=np.random.randint(
                0,
                1_000_000
            )
        )

        candidate_df = pd.concat(
            [candidate_df, fallback],
            ignore_index=True
        )

        candidate_df = candidate_df.drop_duplicates(
            subset=["title", "price", "area"],
            keep="first"
        )

    return candidate_df


# ============================================================
# 7. GENERATE USER-PROPERTY INTERACTIONS
# ============================================================

print("\n[7/8] Creating RL interaction dataset...")

interactions = []

total_users = len(users)

for user_index, user in users.iterrows():

    candidates = get_candidates(
        user,
        properties,
        CANDIDATES_PER_USER
    )

    for _, property_row in candidates.iterrows():

        reward = calculate_reward(
            user,
            property_row
        )

        interaction = {

            # ------------------------------
            # USER INFORMATION
            # ------------------------------

            "user_id": user["user_id"],

            # ------------------------------
            # PROPERTY INFORMATION
            # ------------------------------

            "property_id": int(property_row.name),

            "title": property_row["title"],

            # ------------------------------
            # PROPERTY FEATURES
            # ------------------------------

            "price": float(property_row["price"]),

            "area": float(property_row["area"]),

            "price_per_sqft": float(
                property_row["price_per_sqft"]
            ),

            "locality": property_row["locality"],

            "city": property_row["city"],

            "property_type": property_row["property_type"],

            "bedroom_num": float(
                property_row["bedroom_num"]
            ),

            "bathroom_num": float(
                property_row["bathroom_num"]
            ),

            "balcony_num": float(
                property_row["balcony_num"]
            ),

            "furnished": property_row["furnished"],

            "age": float(
                property_row["age"]
            ),

            # ------------------------------
            # USER PREFERENCES
            # ------------------------------

            "budget_max": float(
                user["budget_max"]
            ),

            "min_area": float(
                user["min_area"]
            ),

            "max_area": float(
                user["max_area"]
            ),

            "bedroom_pref": float(
                user["bedroom_pref"]
            ),

            "bathroom_pref": float(
                user["bathroom_pref"]
            ),

            "balcony_pref": float(
                user["balcony_pref"]
            ),

            "locality_pref": user["locality_pref"],

            "city_pref": user["city_pref"],

            "property_type_pref": (
                user["property_type_pref"]
            ),

            "furnished_pref": user["furnished_pref"],

            "max_age": float(
                user["max_age"]
            ),

            # ------------------------------
            # RL REWARD
            # ------------------------------

            "reward": reward
        }

        interactions.append(interaction)


    # Progress indicator
    if (user_index + 1) % 500 == 0:

        print(
            f"Processed users: "
            f"{user_index + 1:,} / {total_users:,}"
        )


# ============================================================
# 8. SAVE RESULTS
# ============================================================

print("\n[8/8] Saving RL environment data...")

interactions_df = pd.DataFrame(interactions)

interactions_df.to_csv(
    OUTPUT_INTERACTIONS,
    index=False
)


# ============================================================
# SAVE CONFIGURATION
# ============================================================

config = {

    "property_file": PROPERTY_FILE,

    "user_file": USER_FILE,

    "property_count": int(len(properties)),

    "user_count": int(len(users)),

    "candidate_count_per_user": (
        CANDIDATES_PER_USER
    ),

    "interaction_count": (
        int(len(interactions_df))
    ),

    "reward_range": {
        "minimum": 0.0,
        "maximum": 1.0
    },

    "reward_weights": {

        "budget": 0.20,

        "area": 0.12,

        "bedroom": 0.15,

        "bathroom": 0.08,

        "balcony": 0.04,

        "locality": 0.15,

        "city": 0.08,

        "property_type": 0.07,

        "furnished": 0.06,

        "age": 0.05
    },

    "description": (
        "Candidate properties are generated from the "
        "real-estate dataset for each simulated user. "
        "Each user-property pair receives a normalized "
        "suitability reward between 0 and 1."
    )
}

with open(
    OUTPUT_CONFIG,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        config,
        f,
        indent=4
    )


# ============================================================
# FINAL REPORT
# ============================================================

print("\n" + "=" * 75)
print("RL ENVIRONMENT CREATION COMPLETE")
print("=" * 75)

print(
    f"\nProperty records      : "
    f"{len(properties):,}"
)

print(
    f"Simulated users       : "
    f"{len(users):,}"
)

print(
    f"Interactions created  : "
    f"{len(interactions_df):,}"
)

print(
    f"Average reward        : "
    f"{interactions_df['reward'].mean():.4f}"
)

print(
    f"Minimum reward        : "
    f"{interactions_df['reward'].min():.4f}"
)

print(
    f"Maximum reward        : "
    f"{interactions_df['reward'].max():.4f}"
)


# ============================================================
# REWARD DISTRIBUTION
# ============================================================

print("\nReward distribution:")

reward_bins = pd.cut(
    interactions_df["reward"],
    bins=[
        -0.001,
        0.20,
        0.40,
        0.60,
        0.80,
        1.00
    ],
    labels=[
        "0.00 - 0.20",
        "0.20 - 0.40",
        "0.40 - 0.60",
        "0.60 - 0.80",
        "0.80 - 1.00"
    ]
)

distribution = (
    reward_bins
    .value_counts()
    .sort_index()
)

print(distribution)


# ============================================================
# SHOW EXAMPLES
# ============================================================

print("\n" + "=" * 75)
print("SAMPLE USER-PROPERTY INTERACTIONS")
print("=" * 75)

# Pick a random user
sample_user_id = users.iloc[0]["user_id"]

sample_rows = interactions_df[
    interactions_df["user_id"] == sample_user_id
].sort_values(
    "reward",
    ascending=False
).head(5)


for rank, (_, row) in enumerate(
    sample_rows.iterrows(),
    start=1
):

    print("\n" + "-" * 60)

    print(
        f"Rank #{rank}"
    )

    print(
        f"User ID       : {row['user_id']}"
    )

    print(
        f"Property      : {row['title']}"
    )

    print(
        f"Price         : ₹{row['price']:,.0f}"
    )

    print(
        f"Area          : {row['area']:,.0f} sq.ft"
    )

    print(
        f"Location      : "
        f"{row['locality']}, {row['city']}"
    )

    print(
        f"BHK           : {row['bedroom_num']:.0f}"
    )

    print(
        f"Furnished     : {row['furnished']}"
    )

    print(
        f"Reward        : {row['reward']:.4f}"
    )


# ============================================================
# OUTPUT FILES
# ============================================================

print("\n" + "=" * 75)

print("FILES CREATED:")

print(
    f"1. {OUTPUT_INTERACTIONS}"
)

print(
    f"2. {OUTPUT_CONFIG}"
)

print("\nThe interaction dataset is now ready for")
print("the RL-agent training stage.")

print("=" * 75)
