import os
import json
import joblib
import pandas as pd


INPUT_FILE = "DATA_ML/normal_validation_features.csv"

FEATURE_COLUMNS = [
    "event_count",
    "failed_login_count",
    "download_total",
    "records_accessed_total",
    "vip_access_count",
    "unknown_ip_count",
    "outside_hours_count",
    "unique_ip_count",
    "first_activity_hour",
    "last_activity_hour",
]

ROLES = [
    "Teller",
    "CustomerService",
    "Manager"
]

# Bottom 5% of NORMAL validation scores
# will define our initial anomaly threshold.
NORMAL_FALSE_POSITIVE_RATE = 0.05


print("Loading NORMAL validation features...")

df = pd.read_csv(INPUT_FILE)

thresholds = {}
all_results = []


for role in ROLES:

    print("\n" + "=" * 60)
    print(f"CALIBRATING ROLE: {role}")
    print("=" * 60)

    role_df = df[df["role"] == role].copy()

    print("Validation rows:", len(role_df))
    print("Unique users:", role_df["user_id"].nunique())

    model_file = f"MODELS/{role}_isolation_forest.pkl"
    scaler_file = f"MODELS/{role}_scaler.pkl"

    model = joblib.load(model_file)
    scaler = joblib.load(scaler_file)

    X = role_df[FEATURE_COLUMNS]

    X_scaled = scaler.transform(X)

    # Higher score = more normal
    # Lower score = more anomalous
    role_df["anomaly_score"] = model.decision_function(
        X_scaled
    )

    threshold = role_df["anomaly_score"].quantile(
        NORMAL_FALSE_POSITIVE_RATE
    )

    thresholds[role] = float(threshold)

    role_df["calibrated_prediction"] = (
        role_df["anomaly_score"] < threshold
    ).astype(int)

    flagged = role_df[
        "calibrated_prediction"
    ].sum()

    print(
        "Score minimum:",
        round(role_df["anomaly_score"].min(), 4)
    )

    print(
        "Score mean:",
        round(role_df["anomaly_score"].mean(), 4)
    )

    print(
        "Score maximum:",
        round(role_df["anomaly_score"].max(), 4)
    )

    print(
        "5th percentile threshold:",
        round(threshold, 4)
    )

    print(
        "Normal validation rows flagged:",
        flagged,
        "of",
        len(role_df)
    )

    all_results.append(role_df)


# ----------------------------------------------
# Save thresholds
# ----------------------------------------------

os.makedirs("MODELS", exist_ok=True)

with open(
    "MODELS/role_thresholds.json",
    "w"
) as file:

    json.dump(
        thresholds,
        file,
        indent=4
    )


# ----------------------------------------------
# Save validation results
# ----------------------------------------------

validation_results = pd.concat(
    all_results,
    ignore_index=True
)

validation_results.to_csv(
    "DATA_ML/validation_results.csv",
    index=False
)


# ----------------------------------------------
# Final summary
# ----------------------------------------------

print("\n" + "=" * 60)
print("THRESHOLD CALIBRATION COMPLETED")
print("=" * 60)

for role, threshold in thresholds.items():

    print(
        f"{role}: {threshold:.4f}"
    )

print("\nThresholds saved to:")
print("MODELS/role_thresholds.json")

print("\nValidation results saved to:")
print("DATA_ML/validation_results.csv")