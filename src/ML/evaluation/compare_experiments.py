import json
import pandas as pd


EXPERIMENTS = [
    "exp01_obvious",
    "exp02_subtle"
]

rows = []

for experiment_name in EXPERIMENTS:

    config_file = (
        f"DATA_ML/experiments/"
        f"{experiment_name}/experiment_config.json"
    )

    with open(config_file, "r") as file:
        config = json.load(file)

    result = config["results"]

    rows.append({
        "experiment": experiment_name,
        "description": config["description"],
        "normal_cases": config["test_data"]["normal_cases"],
        "anomaly_cases": config["test_data"]["anomaly_cases"],
        "TN": result["true_negative"],
        "FP": result["false_positive"],
        "FN": result["false_negative"],
        "TP": result["true_positive"],
        "accuracy": result["accuracy"],
        "precision": result["precision"],
        "recall": result["recall"],
        "f1_score": result["f1_score"]
    })


df = pd.DataFrame(rows)

print("\n" + "=" * 90)
print("EXPERIMENT COMPARISON")
print("=" * 90)

print(
    df[
        [
            "experiment",
            "accuracy",
            "precision",
            "recall",
            "f1_score",
            "FP",
            "FN"
        ]
    ].to_string(index=False)
)


output_file = (
    "DATA_ML/experiments/"
    "experiment_comparison.csv"
)

df.to_csv(
    output_file,
    index=False
)

print("\nSaved to:")
print(output_file)