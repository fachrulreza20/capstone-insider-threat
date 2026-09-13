import sys
import pandas as pd

from src.ML.features.feature_engineering import create_user_day_features


if len(sys.argv) != 2:
    raise ValueError(
        "Usage: python -m src.ML.features.generate_experiment_features <experiment_name>"
    )

experiment_name = sys.argv[1]

input_file = (
    f"DATA_ML/experiments/{experiment_name}/raw_logs.csv"
)

output_file = (
    f"DATA_ML/experiments/{experiment_name}/features.csv"
)


print("Experiment:", experiment_name)
print("Loading raw logs...")

df = pd.read_csv(input_file)

print("Raw rows:", len(df))
print("Unique users:", df["user_id"].nunique())

print("\nCreating behavioural features...")

features = create_user_day_features(df)

features = features.sort_values(
    by=["user_id", "date"]
).reset_index(drop=True)

features.to_csv(
    output_file,
    index=False
)

print("\nFeatures created.")
print("User-day rows:", len(features))

print("\nRows per role:")
print(features["role"].value_counts())

print("\nSaved to:")
print(output_file)