import os
import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

INPUT_FILE = "DATA_ML/normal_train_features.csv"

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


# --------------------------------------------------
# 2. Load normal training data
# --------------------------------------------------

print("Loading NORMAL training features...")

df = pd.read_csv(INPUT_FILE)

print("Total training rows:", len(df))
print("Unique users:", df["user_id"].nunique())

print("\nRows per role:")
print(df["role"].value_counts())


# --------------------------------------------------
# 3. Prepare output folders
# --------------------------------------------------

os.makedirs("MODELS", exist_ok=True)

all_results = []


# --------------------------------------------------
# 4. Train one model per role
# --------------------------------------------------

for role in ROLES:

    print("\n" + "=" * 60)
    print(f"TRAINING ROLE: {role}")
    print("=" * 60)

    role_df = df[df["role"] == role].copy()

    print("Training rows:", len(role_df))
    print("Unique users:", role_df["user_id"].nunique())

    if len(role_df) == 0:
        print("No data found for this role. Skipping.")
        continue

    # Select behavioural features
    X = role_df[FEATURE_COLUMNS]

    # ----------------------------------------------
    # Scale features
    # ----------------------------------------------

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    # ----------------------------------------------
    # Train Isolation Forest
    # ----------------------------------------------

    model = IsolationForest(
        n_estimators=200,
        contamination="auto",
        random_state=42
    )

    model.fit(X_scaled)

    # ----------------------------------------------
    # Calculate anomaly scores
    # ----------------------------------------------

    role_df["anomaly_score"] = model.decision_function(X_scaled)

    role_df["model_prediction"] = model.predict(X_scaled)

    # Isolation Forest:
    #  1 = normal
    # -1 = anomaly

    normal_count = (role_df["model_prediction"] == 1).sum()
    anomaly_count = (role_df["model_prediction"] == -1).sum()

    # ----------------------------------------------
    # Save model and scaler
    # ----------------------------------------------

    safe_role_name = role.replace(" ", "_")

    model_file = (
        f"MODELS/{safe_role_name}_isolation_forest.pkl"
    )

    scaler_file = (
        f"MODELS/{safe_role_name}_scaler.pkl"
    )

    joblib.dump(model, model_file)
    joblib.dump(scaler, scaler_file)

    # ----------------------------------------------
    # Print role summary
    # ----------------------------------------------

    print("\nTraining completed for:", role)

    print(
        "Anomaly score range:",
        round(role_df["anomaly_score"].min(), 4),
        "to",
        round(role_df["anomaly_score"].max(), 4)
    )

    print(
        "Model classified as NORMAL:",
        normal_count
    )

    print(
        "Model classified as ANOMALY:",
        anomaly_count
    )

    print("Model saved to:", model_file)
    print("Scaler saved to:", scaler_file)

    all_results.append(role_df)


# --------------------------------------------------
# 5. Save combined training results
# --------------------------------------------------

combined_results = pd.concat(
    all_results,
    ignore_index=True
)

combined_results.to_csv(
    "DATA_ML/role_specific_training_results.csv",
    index=False
)


# --------------------------------------------------
# 6. Final summary
# --------------------------------------------------

print("\n" + "=" * 60)
print("ALL ROLE-SPECIFIC MODELS TRAINED")
print("=" * 60)

summary = (
    combined_results
    .groupby("role")
    .agg(
        rows=("user_id", "count"),
        users=("user_id", "nunique"),
        score_min=("anomaly_score", "min"),
        score_mean=("anomaly_score", "mean"),
        score_max=("anomaly_score", "max"),
        predicted_anomaly=(
            "model_prediction",
            lambda x: (x == -1).sum()
        )
    )
    .round(4)
)

print(summary.to_string())

print(
    "\nCombined results saved to:"
)

print(
    "DATA_ML/role_specific_training_results.csv"
)