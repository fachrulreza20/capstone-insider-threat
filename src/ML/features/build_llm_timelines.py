import sys
import pandas as pd


if len(sys.argv) != 3:
    raise ValueError(
        "Usage: python -m src.ML.features.build_llm_timelines "
        "<source_experiment> <output_experiment>"
    )

source_experiment = sys.argv[1]
output_experiment = sys.argv[2]

RAW_FILE = (
    f"DATA_ML/experiments/{source_experiment}/raw_logs.csv"
)

GROUND_TRUTH_FILE = (
    f"DATA_ML/experiments/{source_experiment}/ground_truth.csv"
)

OUTPUT_FILE = (
    f"DATA_ML/experiments/{output_experiment}/llm_inputs.csv"
)


raw = pd.read_csv(RAW_FILE)
truth = pd.read_csv(GROUND_TRUTH_FILE)

raw["timestamp"] = pd.to_datetime(raw["timestamp"])
raw["date"] = raw["timestamp"].dt.date.astype(str)

truth["date"] = truth["date"].astype(str)

records = []


for _, target in truth.iterrows():

    user_id = target["user_id"]
    role = target["role"]
    target_date = target["date"]

    user_logs = raw[
        raw["user_id"] == user_id
    ].copy()

    user_logs = user_logs[
        user_logs["date"] <= target_date
    ].copy()

    # Keep maximum 5 most recent days
    available_dates = (
        sorted(user_logs["date"].unique())[-5:]
    )

    timeline_logs = user_logs[
        user_logs["date"].isin(available_dates)
    ].sort_values("timestamp")

    timeline_lines = []

    for _, event in timeline_logs.iterrows():

        timeline_lines.append(
            (
                f"{event['timestamp']} | "
                f"event={event['event_type']} | "
                f"records={event['records_accessed']} | "
                f"download={event['download_count']} | "
                f"failed_login={event['failed_login']} | "
                f"account={event['account_type']} | "
                f"ip={event['ip_address']} | "
                f"known_ip={event['is_known_ip']}"
            )
        )

    timeline = "\n".join(timeline_lines)

    records.append({
        "user_id": user_id,
        "role": role,
        "target_date": target_date,
        "days_visible": len(available_dates),
        "timeline": timeline
    })


output = pd.DataFrame(records)

output.to_csv(
    OUTPUT_FILE,
    index=False
)

print("=" * 60)
print("LLM TIMELINES CREATED")
print("=" * 60)

print("Rows:", len(output))
print("Unique users:", output["user_id"].nunique())

print("\nDays visible distribution:")
print(output["days_visible"].value_counts().sort_index())

print("\nSaved to:")
print(OUTPUT_FILE)