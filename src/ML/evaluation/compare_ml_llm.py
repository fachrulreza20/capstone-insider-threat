import pandas as pd
from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ============================================================
# CONFIGURATION
# ============================================================

SOURCE_EXP = "exp02_subtle_seed2028"
LLM_EXP = "exp03_llm_seed2028"

BASE_DIR = Path("DATA_ML/experiments")

ML_FILE = (
    BASE_DIR
    / SOURCE_EXP
    / "predictions.csv"
)

GROUND_TRUTH_FILE = (
    BASE_DIR
    / SOURCE_EXP
    / "ground_truth.csv"
)

LLM_FILE = (
    BASE_DIR
    / LLM_EXP
    / "llm_predictions.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / LLM_EXP
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading ML, LLM and ground truth data...")

ml = pd.read_csv(ML_FILE)
truth = pd.read_csv(GROUND_TRUTH_FILE)
llm = pd.read_csv(LLM_FILE)


# ============================================================
# NORMALISE DATE COLUMNS
# ============================================================

ml["date"] = ml["date"].astype(str)
truth["date"] = truth["date"].astype(str)
llm["target_date"] = llm["target_date"].astype(str)


# ============================================================
# SELECT REQUIRED COLUMNS
# ============================================================

ml_small = ml[
    [
        "user_id",
        "date",
        "role",
        "prediction",
        "anomaly_score"
    ]
].copy()

ml_small = ml_small.rename(
    columns={
        "prediction": "ml_prediction"
    }
)


truth_small = truth[
    [
        "user_id",
        "date",
        "role",
        "ground_truth",
        "scenario"
    ]
].copy()


llm_small = llm[
    [
        "user_id",
        "target_date",
        "role",
        "llm_prediction",
        "pattern",
        "reason",
        "evidence"
    ]
].copy()

llm_small = llm_small.rename(
    columns={
        "target_date": "date"
    }
)


# ============================================================
# MERGE
# ============================================================

result = truth_small.merge(
    ml_small,
    on=[
        "user_id",
        "date",
        "role"
    ],
    how="left"
)

result = result.merge(
    llm_small,
    on=[
        "user_id",
        "date",
        "role"
    ],
    how="left"
)


# ============================================================
# VALIDATION
# ============================================================

if result["ml_prediction"].isna().any():

    missing = result[
        result["ml_prediction"].isna()
    ]

    raise ValueError(
        f"{len(missing)} rows are missing ML predictions."
    )


if result["llm_prediction"].isna().any():

    missing = result[
        result["llm_prediction"].isna()
    ]

    raise ValueError(
        f"{len(missing)} rows are missing LLM predictions."
    )


result["ground_truth"] = (
    result["ground_truth"]
    .astype(int)
)

result["ml_prediction"] = (
    result["ml_prediction"]
    .astype(int)
)

result["llm_prediction"] = (
    result["llm_prediction"]
    .astype(int)
)


# ============================================================
# CORRECT / WRONG FLAGS
# ============================================================

result["ml_correct"] = (
    result["ml_prediction"]
    == result["ground_truth"]
)

result["llm_correct"] = (
    result["llm_prediction"]
    == result["ground_truth"]
)


# ============================================================
# COMPARISON CATEGORY
# ============================================================

def comparison_category(row):

    if (
        row["ml_correct"]
        and row["llm_correct"]
    ):
        return "both_correct"

    if (
        row["ml_correct"]
        and not row["llm_correct"]
    ):
        return "ml_only_correct"

    if (
        not row["ml_correct"]
        and row["llm_correct"]
    ):
        return "llm_only_correct"

    return "both_wrong"


result["comparison_category"] = (
    result.apply(
        comparison_category,
        axis=1
    )
)


# ============================================================
# METRIC FUNCTION
# ============================================================

def calculate_metrics(
    y_true,
    y_pred
):

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1]
    ).ravel()

    return {
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "TP": tp,
        "accuracy": accuracy_score(
            y_true,
            y_pred
        ),
        "precision": precision_score(
            y_true,
            y_pred,
            zero_division=0
        ),
        "recall": recall_score(
            y_true,
            y_pred,
            zero_division=0
        ),
        "f1_score": f1_score(
            y_true,
            y_pred,
            zero_division=0
        )
    }


ml_metrics = calculate_metrics(
    result["ground_truth"],
    result["ml_prediction"]
)

llm_metrics = calculate_metrics(
    result["ground_truth"],
    result["llm_prediction"]
)


# ============================================================
# ML FALSE NEGATIVES RECOVERED BY LLM
# ============================================================

ml_false_negatives = result[
    (result["ground_truth"] == 1)
    &
    (result["ml_prediction"] == 0)
].copy()


ml_fn_recovered = ml_false_negatives[
    ml_false_negatives[
        "llm_prediction"
    ] == 1
].copy()


if len(ml_false_negatives) > 0:

    recovery_rate = (
        len(ml_fn_recovered)
        /
        len(ml_false_negatives)
    )

else:

    recovery_rate = 0


# ============================================================
# ML TRUE POSITIVES LOST BY LLM
# ============================================================

ml_true_positives = result[
    (result["ground_truth"] == 1)
    &
    (result["ml_prediction"] == 1)
].copy()


ml_tp_lost_by_llm = ml_true_positives[
    ml_true_positives[
        "llm_prediction"
    ] == 0
].copy()


# ============================================================
# FALSE POSITIVE COMPARISON
# ============================================================

ml_false_positives = result[
    (result["ground_truth"] == 0)
    &
    (result["ml_prediction"] == 1)
].copy()


llm_false_positives = result[
    (result["ground_truth"] == 0)
    &
    (result["llm_prediction"] == 1)
].copy()


llm_new_false_positives = result[
    (result["ground_truth"] == 0)
    &
    (result["ml_prediction"] == 0)
    &
    (result["llm_prediction"] == 1)
].copy()


# ============================================================
# SCENARIO COMPARISON
# ============================================================

scenario_rows = []

for scenario, group in result.groupby(
    "scenario"
):

    anomaly_group = group[
        group["ground_truth"] == 1
    ]

    if len(anomaly_group) > 0:

        ml_detection_rate = (
            anomaly_group[
                "ml_prediction"
            ].mean()
        )

        llm_detection_rate = (
            anomaly_group[
                "llm_prediction"
            ].mean()
        )

    else:

        ml_detection_rate = None
        llm_detection_rate = None


    scenario_rows.append({
        "scenario": scenario,
        "cases": len(group),
        "ground_truth_anomalies": (
            group["ground_truth"].sum()
        ),
        "ml_predicted_anomaly_rate": (
            group["ml_prediction"].mean()
        ),
        "llm_predicted_anomaly_rate": (
            group["llm_prediction"].mean()
        ),
        "ml_detection_rate": (
            ml_detection_rate
        ),
        "llm_detection_rate": (
            llm_detection_rate
        )
    })


scenario_summary = pd.DataFrame(
    scenario_rows
)


# ============================================================
# PRINT MAIN RESULTS
# ============================================================

print("\n" + "=" * 75)
print("ML vs LLM COMPARISON — SEED 2028")
print("=" * 75)


print("\nML PERFORMANCE")

for key, value in ml_metrics.items():

    if key in [
        "accuracy",
        "precision",
        "recall",
        "f1_score"
    ]:

        print(
            f"{key:10}: {value:.4f}"
        )

    else:

        print(
            f"{key:10}: {value}"
        )


print("\nLLM PERFORMANCE")

for key, value in llm_metrics.items():

    if key in [
        "accuracy",
        "precision",
        "recall",
        "f1_score"
    ]:

        print(
            f"{key:10}: {value:.4f}"
        )

    else:

        print(
            f"{key:10}: {value}"
        )


# ============================================================
# PRINT AGREEMENT / DISAGREEMENT
# ============================================================

print("\n" + "=" * 75)
print("AGREEMENT / DISAGREEMENT")
print("=" * 75)

category_counts = (
    result[
        "comparison_category"
    ]
    .value_counts()
)

print(category_counts)


# ============================================================
# PRINT RECOVERY ANALYSIS
# ============================================================

print("\n" + "=" * 75)
print("ML FALSE-NEGATIVE RECOVERY BY LLM")
print("=" * 75)

print(
    "ML false negatives:",
    len(ml_false_negatives)
)

print(
    "Recovered by LLM:",
    len(ml_fn_recovered)
)

print(
    "Recovery rate:",
    f"{recovery_rate:.2%}"
)


print("\nRecovered scenarios:")

if len(ml_fn_recovered) > 0:

    print(
        ml_fn_recovered[
            "scenario"
        ]
        .value_counts()
        .to_string()
    )

else:

    print(
        "None"
    )


# ============================================================
# PRINT TRADE-OFF
# ============================================================

print("\n" + "=" * 75)
print("TRADE-OFF")
print("=" * 75)

print(
    "ML false positives:",
    len(ml_false_positives)
)

print(
    "LLM false positives:",
    len(llm_false_positives)
)

print(
    "New false positives introduced by LLM:",
    len(llm_new_false_positives)
)

print(
    "ML true positives missed by LLM:",
    len(ml_tp_lost_by_llm)
)


# ============================================================
# PRINT SCENARIO SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("PER-SCENARIO COMPARISON")
print("=" * 75)

print(
    scenario_summary
    .round(4)
    .to_string(
        index=False
    )
)


# ============================================================
# SAVE FILES
# ============================================================

result.to_csv(
    OUTPUT_DIR
    / "ml_llm_comparison_detailed.csv",
    index=False
)


scenario_summary.to_csv(
    OUTPUT_DIR
    / "ml_llm_scenario_comparison.csv",
    index=False
)


ml_fn_recovered.to_csv(
    OUTPUT_DIR
    / "ml_false_negatives_recovered_by_llm.csv",
    index=False
)


llm_new_false_positives.to_csv(
    OUTPUT_DIR
    / "llm_new_false_positives.csv",
    index=False
)


summary = pd.DataFrame([
    {
        "model": "Isolation Forest",
        **ml_metrics
    },
    {
        "model": "LLM Temporal",
        **llm_metrics
    }
])


summary.to_csv(
    OUTPUT_DIR
    / "ml_llm_summary.csv",
    index=False
)


print("\nSaved:")

print(
    OUTPUT_DIR
    / "ml_llm_summary.csv"
)

print(
    OUTPUT_DIR
    / "ml_llm_comparison_detailed.csv"
)

print(
    OUTPUT_DIR
    / "ml_llm_scenario_comparison.csv"
)

print(
    OUTPUT_DIR
    / "ml_false_negatives_recovered_by_llm.csv"
)

print(
    OUTPUT_DIR
    / "llm_new_false_positives.csv"
)