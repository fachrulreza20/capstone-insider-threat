import pandas as pd

from src.ML.features.feature_engineering import create_user_day_features


INPUT_FILE = "DATA_ML/validation/normal_validation.csv"
OUTPUT_FILE = "DATA_ML/validation/normal_validation_features.csv"

print("Loading NORMAL validation raw logs...")

df = pd.read_csv(INPUT_FILE)

print("Raw event rows:", len(df))
print("Unique users:", df["user_id"].nunique())


print("\nCreating validation features...")

features = create_user_day_features(df)

features = features.sort_values(
    by=["user_id", "date"]
).reset_index(drop=True)

features.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n" + "=" * 55)
print("VALIDATION FEATURE ENGINEERING COMPLETED")
print("=" * 55)

print("User-day rows:", len(features))

print("\nRows per role:")
print(features["role"].value_counts())

print("\nFirst 5 rows:")
print(features.head().to_string(index=False))

print("\nSaved to:")
print(OUTPUT_FILE)