import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

rows = []

roles = ["Teller", "CustomerService", "Manager"]

role_config = {
    "Teller": {
        "start_hour": 9,
        "end_hour": 17,
        "min_events": 6,
        "max_events": 12,
        "max_download": 5,
        "vip_probability": 0.01,
    },
    "CustomerService": {
        "start_hour": 9,
        "end_hour": 17,
        "min_events": 7,
        "max_events": 14,
        "max_download": 10,
        "vip_probability": 0.03,
    },
    "Manager": {
        "start_hour": 9,
        "end_hour": 17,
        "min_events": 5,
        "max_events": 10,
        "max_download": 20,
        "vip_probability": 0.15,
    },
}

start_date = datetime(2026, 8, 3)

number_of_users = 100
number_of_days = 20

for user_number in range(1, number_of_users + 1):

    user_id = f"USR{user_number:03d}"
    role = random.choice(roles)

    config = role_config[role]

    known_ip = f"10.0.{random.randint(1, 5)}.{random.randint(10, 250)}"

    for day_offset in range(number_of_days):

        current_date = start_date + timedelta(days=day_offset)

        # Skip weekends
        if current_date.weekday() >= 5:
            continue

        start_minutes = random.randint(0, 20)

        login_time = current_date.replace(
            hour=config["start_hour"],
            minute=start_minutes,
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

        number_of_events = random.randint(
            config["min_events"],
            config["max_events"]
        )

        for _ in range(number_of_events):

            event_hour = random.randint(9, 16)
            event_minute = random.randint(0, 59)

            event_time = current_date.replace(
                hour=event_hour,
                minute=event_minute,
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
)

df.to_csv(
    "DATA_ML/normal_train_large.csv",
    index=False
)

print("Normal training dataset generated.")
print("Raw event rows:", len(df))
print("Unique users:", df["user_id"].nunique())
print("Saved to: DATA_ML/normal_train_large.csv")