import pandas as pd


def create_user_day_features(df):
    df = df.copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df["date"] = df["timestamp"].dt.date

    df["hour"] = (
        df["timestamp"].dt.hour
        + df["timestamp"].dt.minute / 60
    )

    df["outside_hours"] = (
        (df["hour"] < 9)
        | (df["hour"] >= 17)
    ).astype(int)

    df["vip_access"] = (
        df["account_type"]
        .astype(str)
        .str.lower()
        .isin(["vip", "sensitive", "high-risk"])
    ).astype(int)

    grouped = (
        df.groupby(["user_id", "date", "role"])
        .agg(
            event_count=("event_type", "count"),
            failed_login_count=("failed_login", "sum"),
            download_total=("download_count", "sum"),
            records_accessed_total=("records_accessed", "sum"),
            vip_access_count=("vip_access", "sum"),
            unknown_ip_count=("is_known_ip", lambda x: (x == 0).sum()),
            outside_hours_count=("outside_hours", "sum"),
            unique_ip_count=("ip_address", "nunique"),
            first_activity_hour=("hour", "min"),
            last_activity_hour=("hour", "max"),
        )
        .reset_index()
    )

    return grouped