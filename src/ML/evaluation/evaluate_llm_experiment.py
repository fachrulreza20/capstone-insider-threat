import pandas as pd
from pathlib import Path
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

SOURCE_EXP = "exp02_subtle_seed2028"
LLM_EXP = "exp03_llm_seed2028"

BASE_DIR = Path("DATA_ML/experiments")

PRED_FILE = BASE_DIR / LLM_EXP / "llm_predictions.csv"
TRUTH_FILE = BASE_DIR / SOURCE_EXP / "ground_truth.csv"
OUTPUT_FILE = BASE_DIR / LLM_EXP / "llm_evaluation_results.csv"

print("Loading LLM predictions and ground truth...")

pred = pd.read_csv(PRED_FILE)
truth = pd.read_csv(TRUTH_FILE)

# Normalise date columns
pred["target_date"] = pred["target_date"].astype(str)

if "date" in truth.columns:
    truth["target_date"] = truth["date"].astype(str)
elif "target_date" in truth.columns:
    truth["target_date"] = truth["target_date"].astype(str)
else:
    raise ValueError("Ground truth file has no date/target_date column.")

# Merge predictions with ground truth
merged = pred.merge(
    truth[["user_id", "target_date", "ground_truth", "scenario"]],
    on=["user_id", "target_date"],
    how="left"
)

if merged["ground_truth"].isna().any():
    missing = merged[merged["ground_truth"].isna()]
    raise ValueError(
        f"{len(missing)} LLM predictions could not be matched to ground truth."
    )

y_true = merged["ground_truth"].astype(int)
y_pred = merged["llm_prediction"].astype(int)

tn, fp, fn, tp = confusion_matrix(
    y_true,
    y_pred,
    labels=[0, 1]
).ravel()

accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred, zero_division=0)
recall = recall_score(y_true, y_pred, zero_division=0)
f1 = f1_score(y_true, y_pred, zero_division=0)

print("\n" + "=" * 65)
print("EXPERIMENT 03 - LLM TEMPORAL EVALUATION")
print("=" * 65)

print("\nConfusion Matrix:")
print([[tn, fp], [fn, tp]])

print(f"\nTrue Negative : {tn}")
print(f"False Positive: {fp}")
print(f"False Negative: {fn}")
print(f"True Positive : {tp}")

print(f"\nAccuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1-score : {f1:.4f}")

print("\nClassification Report:")
print(
    classification_report(
        y_true,
        y_pred,
        target_names=["Normal", "Anomaly"],
        zero_division=0
    )
)

print("\nPerformance by scenario:")

scenario_results = (
    merged.groupby("scenario")
    .agg(
        cases=("ground_truth", "size"),
        ground_truth=("ground_truth", "mean"),
        predicted_anomaly=("llm_prediction", "mean")
    )
)

print(scenario_results.round(4))

merged["correct"] = (
    merged["ground_truth"].astype(int)
    == merged["llm_prediction"].astype(int)
)

merged.to_csv(OUTPUT_FILE, index=False)

print("\nDetailed results saved to:")
print(OUTPUT_FILE)
