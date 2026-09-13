import pandas as pd

from src.ML.features.feature_engineering import create_user_day_features


# 1. Load normal raw training logs
input_file = "DATA_ML/training/normal_train_large.csv"


print("Loading raw training data...")

df = pd.read_csv(input_file)

print("Raw event rows:", len(df))
print("Unique users:", df["user_id"].nunique())


# 2. Convert raw events into user-day behavioural features
print("\nCreating user-day behavioural features...")

features = create_user_day_features(df)


# 3. Sort for easier inspection
features = features.sort_values(
    by=["user_id", "date"]
).reset_index(drop=True)


# 4. Save the resulting feature dataset
output_file = "DATA_ML/training/normal_train_features.csv"

features.to_csv(
    output_file,
    index=False
)


# 5. Display summary
print("\nFeature engineering completed.")
print("User-day rows:", len(features))
print("Columns:", len(features.columns))

print("\nFeature columns:")
for column in features.columns:
    print("-", column)

print("\nFirst 10 rows:")
print(features.head(10).to_string(index=False))

print("\nSaved to:", output_file)