import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

EXPERIMENTS = [
    "exp02_subtle_seed2027",
    "exp02_subtle_seed2028",
    "exp02_subtle_seed2029",
    "exp02_subtle_seed2030",
    "exp02_subtle_seed2031",
]

rows = []

for experiment in EXPERIMENTS:

    file = (
        f"DATA_ML/experiments/"
        f"{experiment}/evaluation_results.csv"
    )

    df = pd.read_csv(file)

    y_true = df["ground_truth"]
    y_pred = df["prediction"]

    rows.append({
        "experiment": experiment,
        "accuracy": accuracy_score(y_true, y_pred),
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
        ),
        "false_positive": (
            (y_true == 0) & (y_pred == 1)
        ).sum(),
        "false_negative": (
            (y_true == 1) & (y_pred == 0)
        ).sum(),
    })

result = pd.DataFrame(rows)

summary = pd.DataFrame({
    "metric": [
        "accuracy",
        "precision",
        "recall",
        "f1_score"
    ],
    "mean": [
        result["accuracy"].mean(),
        result["precision"].mean(),
        result["recall"].mean(),
        result["f1_score"].mean()
    ],
    "std": [
        result["accuracy"].std(),
        result["precision"].std(),
        result["recall"].std(),
        result["f1_score"].std()
    ]
})

print("\nRUN RESULTS")
print(result.round(4).to_string(index=False))

print("\nROBUSTNESS SUMMARY")
print(summary.round(4).to_string(index=False))

result.to_csv(
    "DATA_ML/experiments/"
    "exp02_robustness_runs.csv",
    index=False
)

summary.to_csv(
    "DATA_ML/experiments/"
    "exp02_robustness_summary.csv",
    index=False
)

print("\nSaved:")
print(
    "DATA_ML/experiments/"
    "exp02_robustness_runs.csv"
)
print(
    "DATA_ML/experiments/"
    "exp02_robustness_summary.csv"
)