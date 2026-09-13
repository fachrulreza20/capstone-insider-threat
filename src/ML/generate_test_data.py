import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(2026)

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

start_date = datetime(2026, 9, 14)

# 30 normal users + 15 anomaly users
normal_users_per_role = 10
anomaly_users_per_role = 5
number_of_days = 5

user_counter = 201


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


# ==================================================
# NORMAL USERS
# ==================================================

for role in roles:

    for _ in range(normal_users_per_role):

        user_id = f"TST{user_counter:03d}"
        user_counter += 1

        config = role_config[role]

        known_ip = (
            f"10.2.{random.randint(1, 5)}."
            f"{random.randint(10, 250)}"
        )

        for day_offset in range(number_of_days):

            current_date = start_date + timedelta(days=day_offset)

            if current_date.weekday() >= 5:
                continue

            login_time = current_date.replace(
                hour=9,
                minute=random.randint(0, 20),
                second=0
            )

            add_event(
                login_time,
                user_id,
                role,
                "login",
                0,
                0,
                0,
                "Regular",
                known_ip,
                1
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
                logout_time,
                user_id,
                role,
                "logout",
                0,
                0,
                0,
                "Regular",
                known_ip,
                1
            )

            ground_truth.append({
                "user_id": user_id,
                "date": current_date.date(),
                "role": role,
                "ground_truth": 0,
                "scenario": "normal"
            })


# ==================================================
# ANOMALY USERS
# ==================================================

anomaly_scenarios = [
    "after_hours_exfiltration",
    "credential_compromise",
    "vip_mass_download"
]

for role in roles:

    for anomaly_index in range(anomaly_users_per_role):

        user_id = f"TST{user_counter:03d}"
        user_counter += 1

        scenario = anomaly_scenarios[
            anomaly_index % len(anomaly_scenarios)
        ]

        current_date = start_date + timedelta(
            days=anomaly_index
        )

        known_ip = (
            f"10.2.{random.randint(1, 5)}."
            f"{random.randint(10, 250)}"
        )

        foreign_ip = (
            f"85.{random.randint(10, 200)}."
            f"{random.randint(10, 200)}."
            f"{random.randint(10, 200)}"
        )

        # ------------------------------
        # Scenario 1:
        # After-hours data exfiltration
        # ------------------------------

        if scenario == "after_hours_exfiltration":

            add_event(
                current_date.replace(hour=22, minute=15),
                user_id,
                role,
                "login",
                0,
                0,
                0,
                "Regular",
                known_ip,
                1
            )

            add_event(
                current_date.replace(hour=22, minute=20),
                user_id,
                role,
                "vip_access",
                25,
                0,
                0,
                "VIP",
                known_ip,
                1
            )

            add_event(
                current_date.replace(hour=22, minute=25),
                user_id,
                role,
                "download",
                0,
                250,
                0,
                "VIP",
                known_ip,
                1
            )

        # ------------------------------
        # Scenario 2:
        # Possible credential compromise
        # ------------------------------

        elif scenario == "credential_compromise":

            for minute in [1, 2, 3]:

                add_event(
                    current_date.replace(
                        hour=2,
                        minute=minute
                    ),
                    user_id,
                    role,
                    "login",
                    0,
                    0,
                    1,
                    "Regular",
                    foreign_ip,
                    0
                )

            add_event(
                current_date.replace(hour=2, minute=4),
                user_id,
                role,
                "login_success",
                0,
                0,
                0,
                "Regular",
                foreign_ip,
                0
            )

            add_event(
                current_date.replace(hour=2, minute=8),
                user_id,
                role,
                "vip_access",
                30,
                0,
                0,
                "VIP",
                foreign_ip,
                0
            )

            add_event(
                current_date.replace(hour=2, minute=12),
                user_id,
                role,
                "download",
                0,
                300,
                0,
                "VIP",
                foreign_ip,
                0
            )

        # ------------------------------
        # Scenario 3:
        # VIP mass download
        # ------------------------------

        elif scenario == "vip_mass_download":

            add_event(
                current_date.replace(hour=10, minute=5),
                user_id,
                role,
                "login",
                0,
                0,
                0,
                "Regular",
                known_ip,
                1
            )

            add_event(
                current_date.replace(hour=10, minute=20),
                user_id,
                role,
                "vip_access",
                40,
                0,
                0,
                "VIP",
                known_ip,
                1
            )

            add_event(
                current_date.replace(hour=10, minute=30),
                user_id,
                role,
                "download",
                0,
                200,
                0,
                "VIP",
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
# SAVE FILES
# ==================================================

raw_df = pd.DataFrame(rows)

raw_df = raw_df.sort_values(
    by=["user_id", "timestamp"]
).reset_index(drop=True)

truth_df = pd.DataFrame(ground_truth)

raw_df.to_csv(
    "DATA_ML/test_raw_logs.csv",
    index=False
)

truth_df.to_csv(
    "DATA_ML/test_ground_truth.csv",
    index=False
)


print("=" * 60)
print("TEST DATA GENERATED")
print("=" * 60)

print("Raw event rows:", len(raw_df))
print("Unique test users:", raw_df["user_id"].nunique())

print("\nGround truth rows:", len(truth_df))

print("\nGround truth class distribution:")
print(
    truth_df["ground_truth"].value_counts()
)

print("\nScenario distribution:")
print(
    truth_df["scenario"].value_counts()
)

print("\nSaved:")
print("DATA_ML/test_raw_logs.csv")
print("DATA_ML/test_ground_truth.csv")