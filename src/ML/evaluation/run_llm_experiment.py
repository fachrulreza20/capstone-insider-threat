import os
import sys
import json
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# ARGUMENTS
# ============================================================

if len(sys.argv) != 3:
    raise ValueError(
        "Usage: python -m src.ML.evaluation.run_llm_experiment "
        "<source_experiment> <output_experiment>"
    )

source_experiment = sys.argv[1]
output_experiment = sys.argv[2]


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Keep the same model throughout the FINAL LLM evaluation.
# gpt-5 already worked during our smoke test.
MODEL_NAME = "gpt-5"

SOURCE_RAW_FILE = (
    f"DATA_ML/experiments/{source_experiment}/raw_logs.csv"
)

SOURCE_TRUTH_FILE = (
    f"DATA_ML/experiments/{source_experiment}/ground_truth.csv"
)

OUTPUT_DIR = Path(
    f"DATA_ML/experiments/{output_experiment}"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

LLM_INPUT_FILE = OUTPUT_DIR / "llm_inputs.csv"
LLM_PREDICTION_FILE = OUTPUT_DIR / "llm_predictions.csv"


# ============================================================
# STRUCTURED OUTPUT SCHEMA
# ============================================================

THREAT_SCHEMA = {
    "type": "object",
    "properties": {
        "prediction": {
            "type": "integer",
            "enum": [0, 1]
        },
        "pattern": {
            "type": "string"
        },
        "reason": {
            "type": "string"
        },
        "evidence": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": [
        "prediction",
        "pattern",
        "reason",
        "evidence"
    ],
    "additionalProperties": False
}


# ============================================================
# BUILD MULTI-DAY TIMELINES
# ============================================================

def build_llm_inputs():

    print("Building LLM multi-day timelines...")

    raw = pd.read_csv(SOURCE_RAW_FILE)
    truth = pd.read_csv(SOURCE_TRUTH_FILE)

    raw["timestamp"] = pd.to_datetime(
        raw["timestamp"]
    )

    raw["date"] = (
        raw["timestamp"]
        .dt.date
        .astype(str)
    )

    truth["date"] = truth["date"].astype(str)

    records = []

    for _, target in truth.iterrows():

        user_id = target["user_id"]
        role = target["role"]
        target_date = target["date"]

        user_logs = raw[
            raw["user_id"] == user_id
        ].copy()

        # CRITICAL:
        # Never allow the LLM to see events AFTER the target date.
        user_logs = user_logs[
            user_logs["date"] <= target_date
        ].copy()

        available_dates = sorted(
            user_logs["date"].unique()
        )[-5:]

        timeline_logs = user_logs[
            user_logs["date"].isin(
                available_dates
            )
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

        records.append({
            "user_id": user_id,
            "role": role,
            "target_date": target_date,
            "days_visible": len(
                available_dates
            ),
            "timeline": "\n".join(
                timeline_lines
            )
        })

    output = pd.DataFrame(records)

    output.to_csv(
        LLM_INPUT_FILE,
        index=False
    )

    print(
        "LLM inputs created:",
        len(output)
    )

    print(
        "Saved to:",
        LLM_INPUT_FILE
    )

    return output


# ============================================================
# PROMPT
# ============================================================

def create_prompt(row):

    return f"""
You are analysing employee activity for insider-threat detection.

Employee role:
{row['role']}

Target date:
{row['target_date']}

You are given the employee's recent activity timeline up to the target date.

Your task is to determine whether the behaviour on the TARGET DATE is suspicious.

Important:
- Do not assume malicious intent without evidence.
- Consider changes across multiple days.
- Look for gradual behavioural changes, unusual access patterns,
  abnormal download growth, repeated sensitive access,
  role-inconsistent activity, or other suspicious temporal patterns.
- Activity may still occur during normal working hours and from known IPs.
- Previous days are context only.
- Your classification must specifically refer to the TARGET DATE.

Classification:
- prediction = 0 means normal.
- prediction = 1 means suspicious.

Timeline:
{row['timeline']}
"""


# ============================================================
# LOAD EXISTING RESULTS FOR RESUME
# ============================================================

def load_completed_keys():

    if not LLM_PREDICTION_FILE.exists():
        return set()

    existing = pd.read_csv(
        LLM_PREDICTION_FILE
    )

    if len(existing) == 0:
        return set()

    return set(
        zip(
            existing["user_id"].astype(str),
            existing["target_date"].astype(str)
        )
    )


# ============================================================
# SAVE ONE RESULT IMMEDIATELY
# ============================================================

def append_result(result):

    result_df = pd.DataFrame(
        [result]
    )

    file_exists = (
        LLM_PREDICTION_FILE.exists()
    )

    result_df.to_csv(
        LLM_PREDICTION_FILE,
        mode="a",
        header=not file_exists,
        index=False
    )


# ============================================================
# RUN LLM
# ============================================================

def run_llm():

    if LLM_INPUT_FILE.exists():

        inputs = pd.read_csv(
            LLM_INPUT_FILE
        )

        print(
            "Using existing LLM input file."
        )

    else:

        inputs = build_llm_inputs()

    completed = load_completed_keys()

    print("\n" + "=" * 65)
    print("LLM TEMPORAL EXPERIMENT")
    print("=" * 65)

    print("Source experiment :", source_experiment)
    print("Output experiment :", output_experiment)
    print("Model             :", MODEL_NAME)
    print("Total cases       :", len(inputs))
    print("Already completed :", len(completed))
    print("Remaining         :", len(inputs) - len(completed))

    for index, row in inputs.iterrows():

        key = (
            str(row["user_id"]),
            str(row["target_date"])
        )

        if key in completed:
            continue

        print(
            f"\n[{index + 1}/{len(inputs)}] "
            f"{row['user_id']} | "
            f"{row['target_date']} | "
            f"{row['role']}"
        )

        prompt = create_prompt(row)

        try:

            response = client.responses.create(
                model=MODEL_NAME,
                input=prompt,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "threat_assessment",
                        "description": (
                            "Structured insider-threat "
                            "behaviour assessment."
                        ),
                        "schema": THREAT_SCHEMA,
                        "strict": True
                    }
                }
            )

            parsed = json.loads(
                response.output_text
            )

            result = {
                "user_id": row["user_id"],
                "role": row["role"],
                "target_date": row["target_date"],
                "days_visible": row["days_visible"],
                "llm_prediction": parsed[
                    "prediction"
                ],
                "pattern": parsed[
                    "pattern"
                ],
                "reason": parsed[
                    "reason"
                ],
                "evidence": json.dumps(
                    parsed["evidence"],
                    ensure_ascii=False
                ),
                "model": MODEL_NAME,
                "status": "completed"
            }

            append_result(result)

            print(
                "Prediction:",
                parsed["prediction"],
                "| Pattern:",
                parsed["pattern"]
            )

        except Exception as error:

            print(
                "ERROR:",
                str(error)
            )

            error_result = {
                "user_id": row["user_id"],
                "role": row["role"],
                "target_date": row["target_date"],
                "days_visible": row["days_visible"],
                "llm_prediction": "",
                "pattern": "",
                "reason": "",
                "evidence": "",
                "model": MODEL_NAME,
                "status": (
                    "error: "
                    + str(error)
                )
            }

            append_result(
                error_result
            )

            print(
                "Stopped after error. "
                "Fix the issue and run again."
            )

            return

        # Small pause to reduce burstiness.
        time.sleep(0.2)

    print("\n" + "=" * 65)
    print("LLM RUN COMPLETED")
    print("=" * 65)

    print(
        "Predictions saved to:",
        LLM_PREDICTION_FILE
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_llm()