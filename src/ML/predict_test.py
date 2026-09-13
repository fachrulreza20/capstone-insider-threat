import json
import joblib
import pandas as pd


FEATURE_FILE = "DATA_ML/test_features.csv"

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


print("Loading test features...")

df = pd.read_csv(FEATURE_FILE)


with open(
    "MODELS/role_thresholds.json",
    "r"
) as file:

    thresholds = json.load(file)


prediction_results = []


for role in [
    "Teller",
    "CustomerService",
    "Manager"
]:

    print("\n" + "=" * 60)
    print("PREDICTING ROLE:", role)
    print("=" * 60)

    role_df = df[
        df["role"] == role
    ].copy()

    model = joblib.load(
        f"MODELS/{role}_isolation_forest.pkl"
    )

    scaler = joblib.load(
        f"MODELS/{role}_scaler.pkl"
    )

    X = role_df[FEATURE_COLUMNS]

    X_scaled = scaler.transform(X)

    role_df["anomaly_score"] = (
        model.decision_function(X_scaled)
    )

    threshold = thresholds[role]

    role_df["prediction"] = (
        role_df["anomaly_score"] < threshold
    ).astype(int)

    role_df["threshold"] = threshold

    print("Rows:", len(role_df))
    print(
        "Predicted NORMAL:",
        (role_df["prediction"] == 0).sum()
    )

    print(
        "Predicted ANOMALY:",
        (role_df["prediction"] == 1).sum()
    )

    prediction_results.append(role_df)


result = pd.concat(
    prediction_results,
    ignore_index=True
)

result.to_csv(
    "DATA_ML/test_predictions.csv",
    index=False
)


print("\n" + "=" * 60)
print("PREDICTION COMPLETED")
print("=" * 60)

print("\nTotal predictions:", len(result))

print(
    "\nPredicted class distribution:"
)

print(
    result["prediction"].value_counts()
)

print("\nSaved to:")
print("DATA_ML/test_predictions.csv")