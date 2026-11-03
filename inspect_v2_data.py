
import pandas as pd
import json

# Load the V2 interaction dataset
file_path = "rl_interactions_v2.csv"
df = pd.read_csv(file_path)

print("=" * 60)
print("V2 DATASET INSPECTION")
print("=" * 60)

print("\nShape:", df.shape)

print("\nColumn names and data types:")
print(df.dtypes.to_string())

print("\nFirst 5 rows:")
print(df.head().to_string())

print("\nMissing values per column:")
print(df.isnull().sum().to_string())

print("\nUnique users:", df["user_id"].nunique()
      if "user_id" in df.columns else "Column not named user_id")

print("\nReward statistics:")
if "reward" in df.columns:
    print(df["reward"].describe())
else:
    print("Reward column not found. Check the column names above.")

print("\nInspection complete.")
