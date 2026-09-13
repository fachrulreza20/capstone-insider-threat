import pandas as pd

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


PREDICTION_FILE = "DATA_ML/test_predictions.csv"
GROUND_TRUTH_FILE = "DATA_ML/test_ground_truth.csv"


print("Loading predictions and ground truth...")

pred = pd.read_csv(PREDICTION_FILE)
truth = pd.read_csv(GROUND_TRUTH_FILE)

pred["date"] = pred["date"].astype(str)
truth["date"] = truth["date"].astype(str)


result = pred.merge(
    truth,
    on=[
        "user_id",
        "date",
        "role"
    ],
    how="inner"
)


y_true = result["ground_truth"]
y_pred = result["prediction"]


cm = confusion_matrix(
    y_true,
    y_pred
)

tn, fp, fn, tp = cm.ravel()


accuracy = accuracy_score(
    y_true,
    y_pred
)

precision = precision_score(
    y_true,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_true,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_true,
    y_pred,
    zero_division=0
)


print("\n" + "=" * 60)
print("TEST EVALUATION")
print("=" * 60)

print("\nConfusion Matrix:")
print(cm)

print("\nTrue Negative :", tn)
print("False Positive:", fp)
print("False Negative:", fn)
print("True Positive :", tp)

print("\nAccuracy :", round(accuracy, 4))
print("Precision:", round(precision, 4))
print("Recall   :", round(recall, 4))
print("F1-score :", round(f1, 4))


print("\nClassification Report:")
print(
    classification_report(
        y_true,
        y_pred,
        target_names=[
            "Normal",
            "Anomaly"
        ],
        zero_division=0
    )
)


print("\nPerformance by scenario:")

scenario_summary = (
    result.groupby("scenario")
    .agg(
        cases=("user_id", "count"),
        ground_truth=("ground_truth", "mean"),
        predicted_anomaly=(
            "prediction",
            "mean"
        ),
        average_score=(
            "anomaly_score",
            "mean"
        )
    )
    .round(4)
)

print(
    scenario_summary.to_string()
)


result.to_csv(
    "DATA_ML/test_evaluation_results.csv",
    index=False
)

print("\nDetailed results saved to:")
print(
    "DATA_ML/test_evaluation_results.csv"
)