import sys
import os 

import pandas as pd
import random

from datetime import datetime, timedelta

# random.seed(2027)
# OUTPUT_DIR = "DATA_ML/experiments/exp02_subtle"

if len(sys.argv) != 3:
    raise ValueError(
        "Usage: python -m src.ML.experiments.exp02_subtle "
        "<experiment_name> <seed>"
    )

experiment_name = sys.argv[1]
seed = int(sys.argv[2])

random.seed(seed)

OUTPUT_DIR = f"DATA_ML/experiments/{experiment_name}"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



rows = []
ground_truth = []

roles = ["Teller", "CustomerService", "Manager"]

role_config = {
    "Teller": {
        "min_events": 6,
        "max_events": 12,
        "max_download": 5,
        "vip_probability": 0.01,
    },
    "CustomerService": {
        "min_events": 7,
        "max_events": 14,
        "max_download": 10,
        "vip_probability": 0.03,
    },
    "Manager": {
        "min_events": 5,
        "max_events": 10,
        "max_download": 20,
        "vip_probability": 0.15,
    },
}

start_date = datetime(2026, 9, 21)

normal_users_per_role = 10
subtle_users_per_role = 5
number_of_days = 5

user_counter = 301


def add_event(
    timestamp,
    user_id,
    role,
    event_type,
    records_accessed,
    download_count,
    failed_login,
    account_type,
    ip_address,
    is_known_ip
):
    rows.append({
        "timestamp": timestamp,
        "user_id": user_id,
        "role": role,
        "event_type": event_type,
        "records_accessed": records_accessed,
        "download_count": download_count,
        "failed_login": failed_login,
        "account_type": account_type,
        "ip_address": ip_address,
        "is_known_ip": is_known_ip
    })


def add_normal_day(user_id, role, current_date, known_ip):
    config = role_config[role]

    login_time = current_date.replace(
        hour=9,
        minute=random.randint(0, 20),
        second=0
    )

    add_event(
        login_time, user_id, role, "login",
        0, 0, 0, "Regular", known_ip, 1
    )

    number_of_events = random.randint(
        config["min_events"],
        config["max_events"]
    )

    for _ in range(number_of_events):

        event_time = current_date.replace(
            hour=random.randint(9, 16),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )

        event_type = random.choice([
            "customer_access",
            "customer_access",
            "customer_access",
            "download"
        ])

        account_type = (
            "VIP"
            if random.random() < config["vip_probability"]
            else "Regular"
        )

        if event_type == "download":
            download_count = random.randint(
                1,
                config["max_download"]
            )
            records_accessed = 0
        else:
            download_count = 0
            records_accessed = random.randint(1, 5)

        add_event(
            event_time,
            user_id,
            role,
            event_type,
            records_accessed,
            download_count,
            0,
            account_type,
            known_ip,
            1
        )

    logout_time = current_date.replace(
        hour=16,
        minute=random.randint(30, 59),
        second=0
    )

    add_event(
        logout_time, user_id, role, "logout",
        0, 0, 0, "Regular", known_ip, 1
    )


# ==================================================
# NORMAL USERS
# ==================================================

for role in roles:

    for _ in range(normal_users_per_role):

        user_id = f"SUB{user_counter:03d}"
        user_counter += 1

        known_ip = (
            f"10.3.{random.randint(1, 5)}."
            f"{random.randint(10, 250)}"
        )

        for day_offset in range(number_of_days):

            current_date = start_date + timedelta(days=day_offset)

            if current_date.weekday() >= 5:
                continue

            add_normal_day(
                user_id,
                role,
                current_date,
                known_ip
            )

            ground_truth.append({
                "user_id": user_id,
                "date": current_date.date(),
                "role": role,
                "ground_truth": 0,
                "scenario": "normal"
            })


# ==================================================
# SUBTLE ANOMALY USERS
# ==================================================

subtle_scenarios = [
    "gradual_download_increase",
    "repeated_vip_access",
    "role_deviation",
    "slow_behavioral_drift",
    "unusual_volume_normal_hours"
]

for role in roles:

    for anomaly_index in range(subtle_users_per_role):

        user_id = f"SUB{user_counter:03d}"
        user_counter += 1

        scenario = subtle_scenarios[anomaly_index]

        known_ip = (
            f"10.3.{random.randint(1, 5)}."
            f"{random.randint(10, 250)}"
        )

        for day_offset in range(number_of_days):

            current_date = start_date + timedelta(days=day_offset)

            if current_date.weekday() >= 5:
                continue

            # Start each day from mostly normal behaviour
            add_normal_day(
                user_id,
                role,
                current_date,
                known_ip
            )

            # Only inject stronger subtle deviation on later days
            if day_offset < 2:
                ground_truth.append({
                    "user_id": user_id,
                    "date": current_date.date(),
                    "role": role,
                    "ground_truth": 0,
                    "scenario": "normal_pre_anomaly"
                })
                continue

            # ------------------------------------------
            # Scenario 1: Gradual download increase
            # ------------------------------------------
            if scenario == "gradual_download_increase":

                extra_download = 10 + (day_offset * 5)

                add_event(
                    current_date.replace(hour=15, minute=10),
                    user_id,
                    role,
                    "download",
                    0,
                    extra_download,
                    0,
                    "Regular",
                    known_ip,
                    1
                )

            # ------------------------------------------
            # Scenario 2: Repeated VIP access
            # ------------------------------------------
            elif scenario == "repeated_vip_access":

                for minute in [10, 25, 40]:

                    add_event(
                        current_date.replace(
                            hour=14,
                            minute=minute
                        ),
                        user_id,
                        role,
                        "vip_access",
                        4,
                        0,
                        0,
                        "VIP",
                        known_ip,
                        1
                    )

            # ------------------------------------------
            # Scenario 3: Role deviation
            # ------------------------------------------
            elif scenario == "role_deviation":

                if role == "Teller":
                    extra_records = 18
                    extra_download = 18
                elif role == "CustomerService":
                    extra_records = 25
                    extra_download = 25
                else:
                    extra_records = 35
                    extra_download = 35

                add_event(
                    current_date.replace(hour=13, minute=20),
                    user_id,
                    role,
                    "customer_access",
                    extra_records,
                    0,
                    0,
                    "Regular",
                    known_ip,
                    1
                )

                add_event(
                    current_date.replace(hour=15, minute=30),
                    user_id,
                    role,
                    "download",
                    0,
                    extra_download,
                    0,
                    "Regular",
                    known_ip,
                    1
                )

            # ------------------------------------------
            # Scenario 4: Slow behavioural drift
            # ------------------------------------------
            elif scenario == "slow_behavioral_drift":

                extra_events = day_offset + 1

                for event_number in range(extra_events):

                    add_event(
                        current_date.replace(
                            hour=16,
                            minute=5 + event_number * 5
                        ),
                        user_id,
                        role,
                        "customer_access",
                        5,
                        0,
                        0,
                        "Regular",
                        known_ip,
                        1
                    )

            # ------------------------------------------
            # Scenario 5: Unusual volume in normal hours
            # ------------------------------------------
            elif scenario == "unusual_volume_normal_hours":

                add_event(
                    current_date.replace(hour=11, minute=15),
                    user_id,
                    role,
                    "customer_access",
                    20,
                    0,
                    0,
                    "Regular",
                    known_ip,
                    1
                )

                add_event(
                    current_date.replace(hour=11, minute=40),
                    user_id,
                    role,
                    "download",
                    0,
                    20,
                    0,
                    "Regular",
                    known_ip,
                    1
                )

            ground_truth.append({
                "user_id": user_id,
                "date": current_date.date(),
                "role": role,
                "ground_truth": 1,
                "scenario": scenario
            })


# ==================================================
# SAVE
# ==================================================

raw_df = pd.DataFrame(rows)

raw_df = raw_df.sort_values(
    by=["user_id", "timestamp"]
).reset_index(drop=True)

truth_df = pd.DataFrame(ground_truth)

raw_df.to_csv(
    f"{OUTPUT_DIR}/raw_logs.csv",
    index=False
)

truth_df.to_csv(
    f"{OUTPUT_DIR}/ground_truth.csv",
    index=False
)

print("=" * 60)
print("EXP02 SUBTLE DATA GENERATED")
print("=" * 60)

print("Raw event rows:", len(raw_df))
print("Unique users:", raw_df["user_id"].nunique())

print("\nGround truth rows:", len(truth_df))

print("\nClass distribution:")
print(
    truth_df["ground_truth"].value_counts()
)

print("\nScenario distribution:")
print(
    truth_df["scenario"].value_counts()
)

print("\nSaved:")
print(f"{OUTPUT_DIR}/raw_logs.csv")
print(f"{OUTPUT_DIR}/ground_truth.csv")

print("Experiment:", experiment_name)
print("Random seed:", seed)