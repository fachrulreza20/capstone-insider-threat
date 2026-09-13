import pandas as pd
import random
from datetime import datetime, timedelta

# Different seed from training generator
random.seed(99)

rows = []

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

# Different date period from training data
start_date = datetime(2026, 9, 1)

# New users that were NOT used in training
number_of_days = 10

validation_users = []

user_number = 101

for role in roles:

    for _ in range(10):

        validation_users.append(
            (
                f"VAL{user_number:03d}",
                role
            )
        )

        user_number += 1


for user_id, role in validation_users:

    config = role_config[role]

    known_ip = (
        f"10.1.{random.randint(1, 5)}."
        f"{random.randint(10, 250)}"
    )

    for day_offset in range(number_of_days):

        current_date = start_date + timedelta(days=day_offset)

        # Skip Saturday and Sunday
        if current_date.weekday() >= 5:
            continue

        # ------------------------------
        # LOGIN
        # ------------------------------

        login_time = current_date.replace(
            hour=9,
            minute=random.randint(0, 20),
            second=0
        )

        rows.append({
            "timestamp": login_time,
            "user_id": user_id,
            "role": role,
            "event_type": "login",
            "records_accessed": 0,
            "download_count": 0,
            "failed_login": 0,
            "account_type": "Regular",
            "ip_address": known_ip,
            "is_known_ip": 1
        })

        # ------------------------------
        # NORMAL DAILY ACTIVITIES
        # ------------------------------

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

            if random.random() < config["vip_probability"]:
                account_type = "VIP"
            else:
                account_type = "Regular"

            if event_type == "download":

                download_count = random.randint(
                    1,
                    config["max_download"]
                )

                records_accessed = 0

            else:

                download_count = 0
                records_accessed = random.randint(1, 5)

            rows.append({
                "timestamp": event_time,
                "user_id": user_id,
                "role": role,
                "event_type": event_type,
                "records_accessed": records_accessed,
                "download_count": download_count,
                "failed_login": 0,
                "account_type": account_type,
                "ip_address": known_ip,
                "is_known_ip": 1
            })

        # ------------------------------
        # LOGOUT
        # ------------------------------

        logout_time = current_date.replace(
            hour=16,
            minute=random.randint(30, 59),
            second=0
        )

        rows.append({
            "timestamp": logout_time,
            "user_id": user_id,
            "role": role,
            "event_type": "logout",
            "records_accessed": 0,
            "download_count": 0,
            "failed_login": 0,
            "account_type": "Regular",
            "ip_address": known_ip,
            "is_known_ip": 1
        })


df = pd.DataFrame(rows)

df = df.sort_values(
    by=["user_id", "timestamp"]
).reset_index(drop=True)

output_file = "DATA_ML/normal_validation.csv"

df.to_csv(
    output_file,
    index=False
)

print("=" * 55)
print("NORMAL VALIDATION DATA GENERATED")
print("=" * 55)

print("Raw event rows:", len(df))
print("Unique validation users:", df["user_id"].nunique())

print("\nUsers per role:")
print(
    df[["user_id", "role"]]
    .drop_duplicates()["role"]
    .value_counts()
)

print("\nSaved to:")
print(output_file)