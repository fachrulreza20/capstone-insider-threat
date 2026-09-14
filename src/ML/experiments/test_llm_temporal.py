import os
import json
import pandas as pd

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


INPUT_FILE = (
    "DATA_ML/experiments/"
    "exp03_llm_seed2027/llm_inputs.csv"
)

df = pd.read_csv(INPUT_FILE)

# sample = df.head(3)


GROUND_TRUTH_FILE = (
    "DATA_ML/experiments/"
    "exp02_subtle_seed2027/ground_truth.csv"
)

truth = pd.read_csv(GROUND_TRUTH_FILE)

truth["date"] = truth["date"].astype(str)


truth_small = truth[
    [
        "user_id",
        "date",
        "ground_truth",
        "scenario"
    ]
].copy()

merged = df.merge(
    truth_small,
    left_on=[
        "user_id",
        "target_date"
    ],
    right_on=[
        "user_id",
        "date"
    ],
    how="left"
)


wanted_scenarios = [
    "normal",
    "normal_pre_anomaly",
    "gradual_download_increase",
    "repeated_vip_access",
    "slow_behavioral_drift",
    "role_deviation"
]

samples = []

for scenario in wanted_scenarios:

    scenario_rows = merged[
        merged["scenario"] == scenario
    ]

    if len(scenario_rows) > 0:
        samples.append(
            scenario_rows.iloc[0]
        )

sample = pd.DataFrame(samples)

for _, row in sample.iterrows():

    prompt = f"""
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

Return JSON only with:
{{
  "prediction": 0,
  "pattern": "short pattern name",
  "reason": "brief explanation",
  "evidence": ["evidence 1", "evidence 2"]
}}

0 means normal.
1 means suspicious.

Timeline:
{row['timeline']}
"""

    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )

    print("\n" + "=" * 60)
    print("USER:", row["user_id"])
    print("TARGET DATE:", row["target_date"])
    print("=" * 60)

    print("SCENARIO:", row["scenario"])
    print("GROUND TRUTH:", row["ground_truth"])
    print("LLM OUTPUT:")

    print(response.output_text)