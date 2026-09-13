import pandas as pd

from src.ML.feature_engineering import create_user_day_features


INPUT_FILE = "DATA_ML/test_raw_logs.csv"
OUTPUT_FILE = "DATA_ML/test_features.csv"


print("Loading test raw logs...")

df = pd.read_csv(INPUT_FILE)

print("Raw rows:", len(df))
print("Unique users:", df["user_id"].nunique())


print("\nCreating test behavioural features...")

features = create_user_day_features(df)

features = features.sort_values(
    by=["user_id", "date"]
).reset_index(drop=True)

features.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n" + "=" * 60)
print("TEST FEATURES CREATED")
print("=" * 60)

print("User-day rows:", len(features))

print("\nRows per role:")
print(features["role"].value_counts())

print("\nSaved to:")
print(OUTPUT_FILE)