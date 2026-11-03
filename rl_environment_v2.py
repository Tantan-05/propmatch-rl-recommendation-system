import pandas as pd
import numpy as np
import json
import os

# ============================================================
# REAL ESTATE RL ENVIRONMENT V2
# ============================================================
#
# PROJECT:
# Real Estate Recommendation using Reinforcement Learning
#
# INPUT:
#   filtered_data.csv
#   simulated_users.csv
#
# OUTPUT:
#   rl_interactions_v2.csv
#   rl_environment_v2_config.json
#
# MAIN IMPROVEMENT OVER V1:
#
# V1:
#   Candidate generation was heavily filtered.
#   Most candidates were already good matches.
#
# V2:
#   Every user receives a MIXED candidate pool:
#
#       20 Strong candidates
#       15 Moderate candidates
#       15 Weak/diverse candidates
#
# This creates a more informative reward landscape for
# reinforcement-learning training.
#
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

PROPERTY_FILE = "filtered_data.csv"
USER_FILE = "simulated_users.csv"

OUTPUT_INTERACTIONS = "rl_interactions_v2.csv"
OUTPUT_CONFIG = "rl_environment_v2_config.json"

RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)

# Total candidates per user
TOTAL_CANDIDATES = 50

# Candidate quality distribution
STRONG_CANDIDATES = 20
MODERATE_CANDIDATES = 15
WEAK_CANDIDATES = 15


# ============================================================
# VALIDATE CONFIGURATION
# ============================================================

if (
    STRONG_CANDIDATES
    + MODERATE_CANDIDATES
    + WEAK_CANDIDATES
    != TOTAL_CANDIDATES
):
    raise ValueError(
        "Candidate counts do not add up to TOTAL_CANDIDATES."
    )


# ============================================================
# 1. LOAD DATA
# ============================================================

print("=" * 80)
print("REAL ESTATE RL ENVIRONMENT V2")
print("=" * 80)

print("\n[1/9] Loading datasets...")

properties = pd.read_csv(PROPERTY_FILE)
users = pd.read_csv(USER_FILE)

print(
    f"Properties loaded : "
    f"{len(properties):,}"
)

print(
    f"Users loaded      : "
    f"{len(users):,}"
)


# ============================================================
# 2. VALIDATE PROPERTY DATA
# ============================================================

print("\n[2/9] Validating property dataset...")

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
    column
    for column in required_property_columns
    if column not in properties.columns
]

if missing_property_columns:

    raise ValueError(
        "The following property columns are missing:\n"
        + str(missing_property_columns)
    )


# ============================================================
# 3. VALIDATE USER DATA
# ============================================================

print("[3/9] Validating simulated-user dataset...")

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
    column
    for column in required_user_columns
    if column not in users.columns
]

if missing_user_columns:

    raise ValueError(
        "The following user columns are missing:\n"
        + str(missing_user_columns)
    )


# ============================================================
# 4. CLEAN AND STANDARDIZE DATA
# ============================================================

print("\n[4/9] Cleaning and standardizing data...")


# ------------------------------------------------------------
# PROPERTY NUMERIC COLUMNS
# ------------------------------------------------------------

property_numeric_columns = [
    "price",
    "area",
    "price_per_sqft",
    "bedroom_num",
    "bathroom_num",
    "balcony_num",
    "age"
]

for column in property_numeric_columns:

    properties[column] = pd.to_numeric(
        properties[column],
        errors="coerce"
    )


# ------------------------------------------------------------
# PROPERTY CATEGORICAL COLUMNS
# ------------------------------------------------------------

property_categorical_columns = [
    "locality",
    "city",
    "property_type",
    "furnished"
]

for column in property_categorical_columns:

    properties[column] = (
        properties[column]
        .astype(str)
        .str.strip()
        .str.lower()
    )


# ------------------------------------------------------------
# USER NUMERIC COLUMNS
# ------------------------------------------------------------

user_numeric_columns = [
    "budget_max",
    "min_area",
    "max_area",
    "bedroom_pref",
    "bathroom_pref",
    "balcony_pref",
    "max_age"
]

for column in user_numeric_columns:

    users[column] = pd.to_numeric(
        users[column],
        errors="coerce"
    )


# ------------------------------------------------------------
# USER CATEGORICAL COLUMNS
# ------------------------------------------------------------

user_categorical_columns = [
    "locality_pref",
    "city_pref",
    "property_type_pref",
    "furnished_pref"
]

for column in user_categorical_columns:

    users[column] = (
        users[column]
        .astype(str)
        .str.strip()
        .str.lower()
    )


# ------------------------------------------------------------
# REMOVE INVALID PROPERTY RECORDS
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# REMOVE INVALID USER RECORDS
# ------------------------------------------------------------

users = users.dropna(
    subset=required_user_columns
).copy()


# ------------------------------------------------------------
# RESET INDEX
# ------------------------------------------------------------

properties.reset_index(
    drop=True,
    inplace=True
)

users.reset_index(
    drop=True,
    inplace=True
)


print(
    f"Usable properties : "
    f"{len(properties):,}"
)

print(
    f"Usable users      : "
    f"{len(users):,}"
)


# ============================================================
# 5. REWARD FUNCTION
# ============================================================
#
# The reward represents:
#
# "How suitable is this property for this user?"
#
# Range:
#
#     0.0 → very poor match
#     1.0 → perfect match
#
# ============================================================

print("\n[5/9] Creating reward function...")


def calculate_reward(user, property_row):
    """
    Calculate the suitability reward for a
    user-property interaction.

    Returns:
        float between 0 and 1
    """

    scores = {}


    # ========================================================
    # BUDGET
    # ========================================================

    price = float(property_row["price"])
    budget = float(user["budget_max"])

    if budget <= 0:

        budget_score = 0.0

    elif price <= budget:

        budget_score = 1.0

    else:

        overshoot = (
            (price - budget)
            / budget
        )

        budget_score = max(
            0.0,
            1.0 - overshoot * 2.0
        )

    scores["budget"] = budget_score


    # ========================================================
    # AREA
    # ========================================================

    area = float(property_row["area"])

    min_area = float(
        user["min_area"]
    )

    max_area = float(
        user["max_area"]
    )

    if min_area <= area <= max_area:

        area_score = 1.0

    elif area < min_area:

        difference = (
            (min_area - area)
            / max(min_area, 1)
        )

        area_score = max(
            0.0,
            1.0 - difference
        )

    else:

        difference = (
            (area - max_area)
            / max(max_area, 1)
        )

        area_score = max(
            0.0,
            1.0 - difference
        )

    scores["area"] = area_score


    # ========================================================
    # BEDROOM
    # ========================================================

    bedroom = float(
        property_row["bedroom_num"]
    )

    bedroom_pref = float(
        user["bedroom_pref"]
    )

    bedroom_difference = abs(
        bedroom - bedroom_pref
    )

    bedroom_score = max(
        0.0,
        1.0 - bedroom_difference * 0.5
    )

    scores["bedroom"] = bedroom_score


    # ========================================================
    # BATHROOM
    # ========================================================

    bathroom = float(
        property_row["bathroom_num"]
    )

    bathroom_pref = float(
        user["bathroom_pref"]
    )

    if bathroom >= bathroom_pref:

        bathroom_score = 1.0

    else:

        difference = (
            bathroom_pref - bathroom
        )

        bathroom_score = max(
            0.0,
            1.0 - difference * 0.5
        )

    scores["bathroom"] = bathroom_score


    # ========================================================
    # BALCONY
    # ========================================================

    balcony = float(
        property_row["balcony_num"]
    )

    balcony_pref = float(
        user["balcony_pref"]
    )

    if balcony >= balcony_pref:

        balcony_score = 1.0

    else:

        difference = (
            balcony_pref - balcony
        )

        balcony_score = max(
            0.0,
            1.0 - difference * 0.4
        )

    scores["balcony"] = balcony_score


    # ========================================================
    # LOCALITY
    # ========================================================

    property_locality = str(
        property_row["locality"]
    )

    user_locality = str(
        user["locality_pref"]
    )

    if property_locality == user_locality:

        locality_score = 1.0

    else:

        locality_score = 0.0

    scores["locality"] = locality_score


    # ========================================================
    # CITY
    # ========================================================

    property_city = str(
        property_row["city"]
    )

    user_city = str(
        user["city_pref"]
    )

    if property_city == user_city:

        city_score = 1.0

    else:

        city_score = 0.0

    scores["city"] = city_score


    # ========================================================
    # PROPERTY TYPE
    # ========================================================

    property_type = str(
        property_row["property_type"]
    )

    user_property_type = str(
        user["property_type_pref"]
    )

    if property_type == user_property_type:

        property_type_score = 1.0

    else:

        property_type_score = 0.0

    scores["property_type"] = (
        property_type_score
    )


    # ========================================================
    # FURNISHING
    # ========================================================

    furnished = str(
        property_row["furnished"]
    )

    user_furnished = str(
        user["furnished_pref"]
    )

    if furnished == user_furnished:

        furnished_score = 1.0

    else:

        furnished_score = 0.0

    scores["furnished"] = (
        furnished_score
    )


    # ========================================================
    # PROPERTY AGE
    # ========================================================

    age = float(
        property_row["age"]
    )

    max_age = float(
        user["max_age"]
    )

    if max_age <= 0:

        age_score = 0.0

    elif age <= max_age:

        age_score = 1.0

    else:

        excess_age = (
            (age - max_age)
            / max_age
        )

        age_score = max(
            0.0,
            1.0 - excess_age
        )

    scores["age"] = age_score


    # ========================================================
    # WEIGHTS
    # ========================================================
    #
    # Total = 1.00
    #
    # Higher weights = greater importance.
    #
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


    # ========================================================
    # FINAL REWARD
    # ========================================================

    reward = 0.0

    for feature in weights:

        reward += (
            scores[feature]
            * weights[feature]
        )


    return float(
        np.clip(
            reward,
            0.0,
            1.0
        )
    )


# ============================================================
# 6. CANDIDATE QUALITY SCORE
# ============================================================
#
# This score is ONLY used to identify strong/moderate/weak
# candidates.
#
# The actual reward is calculated separately using the
# calculate_reward() function.
#
# ============================================================

print("\n[6/9] Preparing candidate-selection logic...")


def candidate_quality_score(
    user,
    property_row
):
    """
    Lightweight suitability score used only
    for candidate pool construction.
    """

    score = 0.0


    # ------------------------------
    # Budget
    # ------------------------------

    if property_row["price"] <= user["budget_max"]:

        score += 3.0

    else:

        overshoot = (
            property_row["price"]
            - user["budget_max"]
        ) / user["budget_max"]

        if overshoot <= 0.15:

            score += 1.0


    # ------------------------------
    # Area
    # ------------------------------

    if (
        user["min_area"]
        <= property_row["area"]
        <= user["max_area"]
    ):

        score += 2.0

    else:

        area_difference = min(
            abs(
                property_row["area"]
                - user["min_area"]
            ),
            abs(
                property_row["area"]
                - user["max_area"]
            )
        )

        relative_difference = (
            area_difference
            / max(
                user["max_area"],
                1
            )
        )

        if relative_difference <= 0.20:

            score += 0.75


    # ------------------------------
    # Bedroom
    # ------------------------------

    bedroom_difference = abs(
        property_row["bedroom_num"]
        - user["bedroom_pref"]
    )

    if bedroom_difference == 0:

        score += 2.0

    elif bedroom_difference == 1:

        score += 0.75


    # ------------------------------
    # Bathroom
    # ------------------------------

    if (
        property_row["bathroom_num"]
        >= user["bathroom_pref"]
    ):

        score += 1.0


    # ------------------------------
    # Balcony
    # ------------------------------

    if (
        property_row["balcony_num"]
        >= user["balcony_pref"]
    ):

        score += 0.5


    # ------------------------------
    # Locality
    # ------------------------------

    if (
        property_row["locality"]
        == user["locality_pref"]
    ):

        score += 3.0


    # ------------------------------
    # City
    # ------------------------------

    if (
        property_row["city"]
        == user["city_pref"]
    ):

        score += 2.0


    # ------------------------------
    # Property type
    # ------------------------------

    if (
        property_row["property_type"]
        == user["property_type_pref"]
    ):

        score += 1.5


    # ------------------------------
    # Furnishing
    # ------------------------------

    if (
        property_row["furnished"]
        == user["furnished_pref"]
    ):

        score += 1.0


    # ------------------------------
    # Age
    # ------------------------------

    if (
        property_row["age"]
        <= user["max_age"]
    ):

        score += 1.0


    return score


# ============================================================
# 7. GENERATE BALANCED CANDIDATE POOL
# ============================================================
#
# IMPORTANT:
#
# We create candidates in THREE groups:
#
# STRONG:
#   Properties that closely match the user.
#
# MODERATE:
#   Properties that satisfy some preferences.
#
# WEAK:
#   Properties that are substantially different.
#
# This creates a richer learning environment.
#
# ============================================================

print("\n[7/9] Generating balanced candidate pools...")


def get_balanced_candidates(
    user,
    properties
):

    # --------------------------------------------------------
    # Calculate lightweight suitability score for all
    # properties.
    #
    # This is computationally simple enough for our dataset.
    # --------------------------------------------------------

    scores = []

    for index, property_row in properties.iterrows():

        score = candidate_quality_score(
            user,
            property_row
        )

        scores.append(score)


    scored = properties.copy()

    scored["_candidate_score"] = scores


    # --------------------------------------------------------
    # Sort by suitability.
    # --------------------------------------------------------

    scored = scored.sort_values(
        "_candidate_score",
        ascending=False
    )


    # --------------------------------------------------------
    # STRONG CANDIDATES
    #
    # Take from the upper portion of the ranking.
    # --------------------------------------------------------

    strong_pool_size = min(
        max(
            STRONG_CANDIDATES * 3,
            100
        ),
        len(scored)
    )

    strong_pool = scored.head(
        strong_pool_size
    )

    if len(strong_pool) > STRONG_CANDIDATES:

        strong = strong_pool.sample(
            n=STRONG_CANDIDATES,
            random_state=np.random.randint(
                0,
                1_000_000
            )
        )

    else:

        strong = strong_pool.copy()


    # --------------------------------------------------------
    # MODERATE CANDIDATES
    #
    # Take from the middle of the suitability ranking.
    # --------------------------------------------------------

    middle_start = int(
        len(scored) * 0.30
    )

    middle_end = int(
        len(scored) * 0.70
    )

    if middle_end <= middle_start:

        middle_start = 0
        middle_end = len(scored)


    moderate_pool = scored.iloc[
        middle_start:middle_end
    ]


    if len(moderate_pool) >= MODERATE_CANDIDATES:

        moderate = moderate_pool.sample(
            n=MODERATE_CANDIDATES,
            random_state=np.random.randint(
                0,
                1_000_000
            )
        )

    else:

        moderate = moderate_pool.copy()


    # --------------------------------------------------------
    # WEAK CANDIDATES
    #
    # Take from the lower portion of the ranking.
    # --------------------------------------------------------

    weak_start = int(
        len(scored) * 0.75
    )

    weak_pool = scored.iloc[
        weak_start:
    ]


    if len(weak_pool) >= WEAK_CANDIDATES:

        weak = weak_pool.sample(
            n=WEAK_CANDIDATES,
            random_state=np.random.randint(
                0,
                1_000_000
            )
        )

    else:

        weak = weak_pool.copy()


    # --------------------------------------------------------
    # Combine all three groups.
    # --------------------------------------------------------

    candidates = pd.concat(
        [
            strong,
            moderate,
            weak
        ],
        ignore_index=True
    )


    # --------------------------------------------------------
    # Remove duplicates.
    # --------------------------------------------------------

    candidates = candidates.drop_duplicates(
        subset=[
            "title",
            "price",
            "area",
            "locality"
        ]
    )


    # --------------------------------------------------------
    # If duplicates caused us to fall below 50 candidates,
    # randomly supplement from the remaining dataset.
    # --------------------------------------------------------

    if len(candidates) < TOTAL_CANDIDATES:

        remaining = scored[
            ~scored.index.isin(
                candidates.index
            )
        ]

        required = (
            TOTAL_CANDIDATES
            - len(candidates)
        )

        if len(remaining) >= required:

            supplement = remaining.sample(
                n=required,
                random_state=np.random.randint(
                    0,
                    1_000_000
                )
            )

        else:

            supplement = remaining.copy()


        candidates = pd.concat(
            [
                candidates,
                supplement
            ],
            ignore_index=True
        )


    # --------------------------------------------------------
    # Final random shuffle.
    #
    # We don't want the RL training data to have all strong
    # candidates first, then moderate, then weak.
    # --------------------------------------------------------

    candidates = candidates.sample(
        frac=1,
        random_state=np.random.randint(
            0,
            1_000_000
        )
    ).reset_index(
        drop=True
    )


    # --------------------------------------------------------
    # Remove temporary score.
    # --------------------------------------------------------

    candidates = candidates.drop(
        columns=["_candidate_score"],
        errors="ignore"
    )


    return candidates.head(
        TOTAL_CANDIDATES
    )


# ============================================================
# 8. CREATE USER-PROPERTY INTERACTIONS
# ============================================================

print("\n[8/9] Creating RL interaction dataset...")

interactions = []

total_users = len(users)

for user_index, user in users.iterrows():

    candidates = get_balanced_candidates(
        user,
        properties
    )


    for _, property_row in candidates.iterrows():

        reward = calculate_reward(
            user,
            property_row
        )


        interaction = {

            # ==================================================
            # USER
            # ==================================================

            "user_id": user["user_id"],


            # ==================================================
            # PROPERTY
            # ==================================================

            "property_id": int(
                property_row.name
            ),

            "title": property_row["title"],


            # ==================================================
            # PROPERTY FEATURES
            # ==================================================

            "price": float(
                property_row["price"]
            ),

            "area": float(
                property_row["area"]
            ),

            "price_per_sqft": float(
                property_row["price_per_sqft"]
            ),

            "locality": property_row["locality"],

            "city": property_row["city"],

            "property_type": (
                property_row["property_type"]
            ),

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


            # ==================================================
            # USER PREFERENCES
            # ==================================================

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

            "locality_pref": (
                user["locality_pref"]
            ),

            "city_pref": (
                user["city_pref"]
            ),

            "property_type_pref": (
                user["property_type_pref"]
            ),

            "furnished_pref": (
                user["furnished_pref"]
            ),

            "max_age": float(
                user["max_age"]
            ),


            # ==================================================
            # RL REWARD
            # ==================================================

            "reward": reward
        }


        interactions.append(
            interaction
        )


    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

    if (
        (user_index + 1) % 250 == 0
        or
        user_index == total_users - 1
    ):

        print(
            f"Processed users: "
            f"{user_index + 1:,} / "
            f"{total_users:,}"
        )


# ============================================================
# CONVERT TO DATAFRAME
# ============================================================

interactions_df = pd.DataFrame(
    interactions
)


# ============================================================
# 9. SAVE OUTPUTS
# ============================================================

print("\n[9/9] Saving V2 outputs...")


# ------------------------------------------------------------
# Save interactions
# ------------------------------------------------------------

interactions_df.to_csv(
    OUTPUT_INTERACTIONS,
    index=False
)


# ------------------------------------------------------------
# Reward statistics
# ------------------------------------------------------------

reward_series = interactions_df[
    "reward"
]


# ------------------------------------------------------------
# Reward distribution
# ------------------------------------------------------------

reward_bins = pd.cut(
    reward_series,
    bins=[
        -0.001,
        0.20,
        0.40,
        0.50,
        0.60,
        0.70,
        0.80,
        0.90,
        1.001
    ],
    labels=[
        "0.00-0.20",
        "0.20-0.40",
        "0.40-0.50",
        "0.50-0.60",
        "0.60-0.70",
        "0.70-0.80",
        "0.80-0.90",
        "0.90-1.00"
    ]
)

distribution = (
    reward_bins
    .value_counts()
    .sort_index()
)


# ------------------------------------------------------------
# Configuration file
# ------------------------------------------------------------

config = {

    "version": "V2",

    "property_file": PROPERTY_FILE,

    "user_file": USER_FILE,

    "property_count": int(
        len(properties)
    ),

    "user_count": int(
        len(users)
    ),

    "total_candidates_per_user": (
        TOTAL_CANDIDATES
    ),

    "candidate_distribution": {

        "strong": STRONG_CANDIDATES,

        "moderate": MODERATE_CANDIDATES,

        "weak": WEAK_CANDIDATES
    },

    "interaction_count": int(
        len(interactions_df)
    ),

    "reward_statistics": {

        "minimum": float(
            reward_series.min()
        ),

        "maximum": float(
            reward_series.max()
        ),

        "mean": float(
            reward_series.mean()
        ),

        "median": float(
            reward_series.median()
        ),

        "std": float(
            reward_series.std()
        )
    },

    "reward_distribution": {

        str(category): int(count)

        for category, count
        in distribution.items()
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

    "reward_range": {

        "minimum": 0.0,

        "maximum": 1.0
    }
}


with open(
    OUTPUT_CONFIG,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        config,
        file,
        indent=4
    )


# ============================================================
# FINAL REPORT
# ============================================================

print("\n" + "=" * 80)
print("RL ENVIRONMENT V2 COMPLETE")
print("=" * 80)

print(
    f"\nProperties          : "
    f"{len(properties):,}"
)

print(
    f"Users               : "
    f"{len(users):,}"
)

print(
    f"Candidates per user : "
    f"{TOTAL_CANDIDATES}"
)

print(
    f"Total interactions  : "
    f"{len(interactions_df):,}"
)

print("\nReward Statistics")
print("-" * 40)

print(
    f"Minimum : "
    f"{reward_series.min():.4f}"
)

print(
    f"Maximum : "
    f"{reward_series.max():.4f}"
)

print(
    f"Mean    : "
    f"{reward_series.mean():.4f}"
)

print(
    f"Median  : "
    f"{reward_series.median():.4f}"
)

print(
    f"Std     : "
    f"{reward_series.std():.4f}"
)


print("\nReward Distribution")
print("-" * 40)

for category, count in distribution.items():

    percentage = (
        count
        / len(interactions_df)
        * 100
    )

    print(
        f"{category}: "
        f"{count:,} "
        f"({percentage:.2f}%)"
    )


# ============================================================
# SAMPLE USERS
# ============================================================

print("\n" + "=" * 80)
print("SAMPLE USER RECOMMENDATIONS")
print("=" * 80)


sample_user_ids = (
    users["user_id"]
    .head(5)
    .tolist()
)


for user_id in sample_user_ids:

    user_interactions = (
        interactions_df[
            interactions_df["user_id"]
            == user_id
        ]
        .sort_values(
            "reward",
            ascending=False
        )
    )


    print(
        f"\nUSER: {user_id}"
    )

    print("-" * 70)


    # Top 3
    print("\nTOP 3:")

    for rank, (_, row) in enumerate(
        user_interactions.head(3).iterrows(),
        start=1
    ):

        print(
            f"\n#{rank} "
            f"{row['title']}"
        )

        print(
            f"  Reward : "
            f"{row['reward']:.4f}"
        )

        print(
            f"  Price  : "
            f"₹{row['price']:,.0f}"
        )

        print(
            f"  Area   : "
            f"{row['area']:,.0f} sq.ft"
        )

        print(
            f"  BHK    : "
            f"{row['bedroom_num']:.0f}"
        )

        print(
            f"  Locality: "
            f"{row['locality']}"
        )


    # Bottom 3
    print("\nBOTTOM 3:")

    for rank, (_, row) in enumerate(
        user_interactions.tail(3)
        .sort_values("reward")
        .iterrows(),
        start=1
    ):

        print(
            f"\n#{rank} "
            f"{row['title']}"
        )

        print(
            f"  Reward : "
            f"{row['reward']:.4f}"
        )

        print(
            f"  Price  : "
            f"₹{row['price']:,.0f}"
        )

        print(
            f"  Area   : "
            f"{row['area']:,.0f} sq.ft"
        )

        print(
            f"  BHK    : "
            f"{row['bedroom_num']:.0f}"
        )

        print(
            f"  Locality: "
            f"{row['locality']}"
        )


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n" + "=" * 80)

print(
    "FILES CREATED:"
)

print(
    f"\n1. {OUTPUT_INTERACTIONS}"
)

print(
    f"2. {OUTPUT_CONFIG}"
)

print(
    "\nIMPORTANT:"
)

print(
    "Do NOT start RL training yet."
)

print(
    "First analyze the V2 reward distribution and "
    "compare it with V1."
)

print(
    "\nV2 is designed to provide the RL agent with "
    "strong, moderate, and weak candidate properties."
)

print("=" * 80)