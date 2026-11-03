import pandas as pd
import numpy as np

# ============================================================
# REWARD ANALYSIS FOR RL INTERACTION DATASET
# ============================================================

INPUT_FILE = "rl_interactions.csv"

print("=" * 80)
print("RL REWARD SYSTEM ANALYSIS")
print("=" * 80)

# ============================================================
# 1. LOAD DATA
# ============================================================

print("\n[1/7] Loading interaction dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Rows loaded    : {len(df):,}")
print(f"Columns loaded : {len(df.columns)}")

required_columns = [
    "user_id",
    "title",
    "price",
    "area",
    "locality",
    "city",
    "property_type",
    "bedroom_num",
    "bathroom_num",
    "balcony_num",
    "furnished",
    "age",
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
    "max_age",
    "reward"
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    raise ValueError(
        f"Missing required columns:\n{missing}"
    )

# ============================================================
# 2. BASIC REWARD STATISTICS
# ============================================================

print("\n[2/7] BASIC REWARD STATISTICS")
print("-" * 80)

reward = pd.to_numeric(df["reward"], errors="coerce")

print(f"Minimum reward : {reward.min():.4f}")
print(f"Maximum reward : {reward.max():.4f}")
print(f"Mean reward    : {reward.mean():.4f}")
print(f"Median reward  : {reward.median():.4f}")
print(f"Std deviation  : {reward.std():.4f}")

print("\nReward percentiles:")

percentiles = reward.quantile(
    [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
)

for p, value in percentiles.items():
    print(f"{int(p * 100):>2}% percentile : {value:.4f}")


# ============================================================
# 3. REWARD DISTRIBUTION
# ============================================================

print("\n[3/7] REWARD DISTRIBUTION")
print("-" * 80)

bins = [
    -0.001,
    0.20,
    0.40,
    0.60,
    0.70,
    0.80,
    0.90,
    1.001
]

labels = [
    "0.00-0.20",
    "0.20-0.40",
    "0.40-0.60",
    "0.60-0.70",
    "0.70-0.80",
    "0.80-0.90",
    "0.90-1.00"
]

df["reward_group"] = pd.cut(
    reward,
    bins=bins,
    labels=labels
)

distribution = (
    df["reward_group"]
    .value_counts()
    .sort_index()
)

for category, count in distribution.items():

    percentage = (count / len(df)) * 100

    print(
        f"{category}: "
        f"{count:,} interactions "
        f"({percentage:.2f}%)"
    )


# ============================================================
# 4. CREATE MATCH INDICATORS
# ============================================================

print("\n[4/7] CHECKING WHETHER PREFERENCE MATCHES INCREASE REWARD")
print("-" * 80)

# Budget match
df["budget_match"] = df["price"] <= df["budget_max"]

# Area match
df["area_match"] = (
    (df["area"] >= df["min_area"]) &
    (df["area"] <= df["max_area"])
)

# Bedroom match
df["bedroom_match"] = (
    df["bedroom_num"] == df["bedroom_pref"]
)

# Bathroom match
df["bathroom_match"] = (
    df["bathroom_num"] >= df["bathroom_pref"]
)

# Balcony match
df["balcony_match"] = (
    df["balcony_num"] >= df["balcony_pref"]
)

# Locality match
df["locality_match"] = (
    df["locality"].astype(str).str.strip().str.lower()
    ==
    df["locality_pref"].astype(str).str.strip().str.lower()
)

# City match
df["city_match"] = (
    df["city"].astype(str).str.strip().str.lower()
    ==
    df["city_pref"].astype(str).str.strip().str.lower()
)

# Property type match
df["property_type_match"] = (
    df["property_type"].astype(str).str.strip().str.lower()
    ==
    df["property_type_pref"].astype(str).str.strip().str.lower()
)

# Furnishing match
df["furnished_match"] = (
    df["furnished"].astype(str).str.strip().str.lower()
    ==
    df["furnished_pref"].astype(str).str.strip().str.lower()
)

# Age match
df["age_match"] = (
    df["age"] <= df["max_age"]
)


match_columns = {
    "Budget": "budget_match",
    "Area": "area_match",
    "Bedroom": "bedroom_match",
    "Bathroom": "bathroom_match",
    "Balcony": "balcony_match",
    "Locality": "locality_match",
    "City": "city_match",
    "Property Type": "property_type_match",
    "Furnishing": "furnished_match",
    "Age": "age_match"
}


for label, column in match_columns.items():

    match_rewards = df.loc[
        df[column] == True,
        "reward"
    ]

    non_match_rewards = df.loc[
        df[column] == False,
        "reward"
    ]

    match_mean = match_rewards.mean()
    non_match_mean = non_match_rewards.mean()

    match_rate = df[column].mean() * 100

    difference = match_mean - non_match_mean

    print(f"\n{label}")

    print(
        f"  Match rate          : "
        f"{match_rate:.2f}%"
    )

    print(
        f"  Avg reward MATCH    : "
        f"{match_mean:.4f}"
    )

    print(
        f"  Avg reward NO MATCH : "
        f"{non_match_mean:.4f}"
    )

    print(
        f"  Reward difference   : "
        f"{difference:+.4f}"
    )


# ============================================================
# 5. HOW MANY PREFERENCES DOES EACH PROPERTY MATCH?
# ============================================================

print("\n[5/7] NUMBER OF MATCHED USER PREFERENCES VS REWARD")
print("-" * 80)

indicator_columns = list(match_columns.values())

df["total_matches"] = (
    df[indicator_columns]
    .astype(int)
    .sum(axis=1)
)

match_summary = (
    df.groupby("total_matches")["reward"]
    .agg(["count", "mean", "min", "max"])
)

print(match_summary.to_string())


# ============================================================
# 6. TOP AND BOTTOM RECOMMENDATIONS FOR SAMPLE USERS
# ============================================================

print("\n[6/7] SAMPLE USER RECOMMENDATION QUALITY")
print("=" * 80)

unique_users = df["user_id"].drop_duplicates()

# Choose first 5 users for reproducibility
sample_users = unique_users.head(5)


def print_property(row, rank_type):

    print("\n" + "-" * 70)

    print(f"{rank_type}")

    print(f"Property         : {row['title']}")
    print(f"Reward           : {row['reward']:.4f}")

    print(
        f"Price            : "
        f"₹{row['price']:,.0f}"
    )

    print(
        f"User Budget      : "
        f"₹{row['budget_max']:,.0f}"
    )

    print(
        f"Area             : "
        f"{row['area']:,.0f} sq.ft"
    )

    print(
        f"Preferred Area   : "
        f"{row['min_area']:,.0f}"
        f" - "
        f"{row['max_area']:,.0f} sq.ft"
    )

    print(
        f"BHK              : "
        f"{row['bedroom_num']:.0f}"
        f" | Preferred: "
        f"{row['bedroom_pref']:.0f}"
    )

    print(
        f"Locality         : "
        f"{row['locality']}"
    )

    print(
        f"Preferred Locality: "
        f"{row['locality_pref']}"
    )

    print(
        f"City             : "
        f"{row['city']}"
    )

    print(
        f"Preferred City   : "
        f"{row['city_pref']}"
    )

    print(
        f"Property Type    : "
        f"{row['property_type']}"
    )

    print(
        f"Preferred Type   : "
        f"{row['property_type_pref']}"
    )

    print(
        f"Furnished        : "
        f"{row['furnished']}"
    )

    print(
        f"Preferred Furnish: "
        f"{row['furnished_pref']}"
    )

    print(
        f"Total Matches    : "
        f"{row['total_matches']}/10"
    )


for user_id in sample_users:

    user_data = df[
        df["user_id"] == user_id
    ].sort_values(
        "reward",
        ascending=False
    )

    print("\n")
    print("=" * 80)
    print(f"USER: {user_id}")
    print("=" * 80)

    best = user_data.iloc[0]
    worst = user_data.iloc[-1]

    print_property(
        best,
        "BEST RECOMMENDATION"
    )

    print_property(
        worst,
        "WORST RECOMMENDATION"
    )


# ============================================================
# 7. AUTOMATIC HEALTH CHECK
# ============================================================

print("\n[7/7] AUTOMATIC REWARD HEALTH CHECK")
print("=" * 80)

mean_reward = reward.mean()
std_reward = reward.std()

high_reward_percentage = (
    (reward >= 0.8).mean() * 100
)

very_high_reward_percentage = (
    (reward >= 0.9).mean() * 100
)

low_reward_percentage = (
    (reward < 0.5).mean() * 100
)


warnings = []

# ------------------------------------------------------------
# Check if rewards are overly concentrated
# ------------------------------------------------------------

if std_reward < 0.08:

    warnings.append(
        "Reward variation is LOW. "
        "Properties may be receiving scores that are too similar."
    )


# ------------------------------------------------------------
# Too many high rewards
# ------------------------------------------------------------

if high_reward_percentage > 70:

    warnings.append(
        "More than 70% of interactions have reward >= 0.80. "
        "The reward function may be too generous."
    )


# ------------------------------------------------------------
# Almost no low rewards
# ------------------------------------------------------------

if low_reward_percentage < 5:

    warnings.append(
        "Less than 5% of interactions have reward below 0.50. "
        "The system may not contain enough poor examples."
    )


# ------------------------------------------------------------
# Check top vs bottom reward difference per user
# ------------------------------------------------------------

user_reward_range = (
    df.groupby("user_id")["reward"]
    .agg(lambda x: x.max() - x.min())
)

average_user_range = user_reward_range.mean()

print(
    f"\nAverage reward                  : "
    f"{mean_reward:.4f}"
)

print(
    f"Reward standard deviation       : "
    f"{std_reward:.4f}"
)

print(
    f"Interactions reward >= 0.80     : "
    f"{high_reward_percentage:.2f}%"
)

print(
    f"Interactions reward >= 0.90     : "
    f"{very_high_reward_percentage:.2f}%"
)

print(
    f"Interactions reward < 0.50      : "
    f"{low_reward_percentage:.2f}%"
)

print(
    f"Average best-worst gap per user : "
    f"{average_user_range:.4f}"
)


if average_user_range < 0.15:

    warnings.append(
        "The difference between each user's best and worst "
        "candidate is small. The RL agent may struggle to "
        "learn meaningful ranking differences."
    )


# ============================================================
# FINAL VERDICT
# ============================================================

print("\n" + "=" * 80)
print("FINAL AUTOMATIC VERDICT")
print("=" * 80)

if len(warnings) == 0:

    print(
        "\n✅ REWARD SYSTEM LOOKS HEALTHY."
    )

    print(
        "\nThe reward values show reasonable variation "
        "and appear suitable for proceeding toward RL training."
    )

else:

    print(
        "\n⚠️ REWARD SYSTEM MAY NEED ADJUSTMENT."
    )

    print("\nDetected issues:")

    for i, warning in enumerate(
        warnings,
        start=1
    ):

        print(
            f"\n{i}. {warning}"
        )


print("\n" + "=" * 80)

print(
    "ANALYSIS COMPLETE."
)

print(
    "Do NOT modify rl_interactions.csv yet."
)

print(
    "Send the terminal output of this script before "
    "starting RL model training."
)

print("=" * 80)