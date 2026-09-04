
import os
import json
import pandas as pd
from datetime import time
 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMPLOYEE_ROLES_PATH = os.path.join(BASE_DIR, "config", "employee_roles.json")
EMPLOYEE_SAVED_IPS_PATH = os.path.join(BASE_DIR, "config", "employee_saved_ips.json")
RAW_LOG_PATH = os.path.join(BASE_DIR, "data", "raw_audit_logs.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "sample_audit_logs.csv")
 
# Heuristic window only - for picking which event to surface as
# representative. rule_engine.py does the real per-role hours check.
HEURISTIC_START = time(9, 0)
HEURISTIC_END = time(17, 0)
 
SENSITIVITY_MAP = {
    "Konglomerat": "HIGH-RISK",
    "Pejabat": "HIGH-RISK",
    "Priority": "Sensitive/VIP",
}
SENSITIVITY_RANK = {"Regular": 0, "Sensitive/VIP": 1, "HIGH-RISK": 2}
 
 
def load_json(path):
    with open(path) as f:
        return json.load(f)
 
 
def load_raw_logs(path):
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["records_count"] = df["records_count"].fillna(0)
    df["activity_date"] = df["timestamp"].dt.date
    return df
 
 
def tag_rows(df, employee_saved_ips):
    df = df.copy()
    df["is_out_of_hours"] = df["timestamp"].dt.time.apply(
        lambda t: t < HEURISTIC_START or t > HEURISTIC_END
    )
    df["is_failed_login"] = df["event_type"] == "login_failed"
    df["is_download"] = df["action"] == "download"
    df["sensitivity_tier"] = df["account_type"].map(SENSITIVITY_MAP).fillna("Regular")
    df["saved_ip"] = df["user_id"].map(lambda u: employee_saved_ips.get(u))
    df["is_unrecognized_ip"] = df["ip_address"] != df["saved_ip"]
    return df
 
 
def pick_representative_timestamp(group):
    out_of_hours = group[group["is_out_of_hours"]]
    chosen = out_of_hours if not out_of_hours.empty else group
    return chosen.sort_values("timestamp").iloc[0]["timestamp"]
 
 
def pick_representative_ip(group):
    unrecognized = group[group["is_unrecognized_ip"]]
    if not unrecognized.empty:
        return unrecognized.sort_values("timestamp").iloc[0]["ip_address"]
    return group.iloc[0]["saved_ip"]
 
 
def pick_representative_sensitivity(group):
    return max(group["sensitivity_tier"], key=lambda t: SENSITIVITY_RANK[t])
 
 
def aggregate(df, employee_roles):
    rows = []
    for (user_id, activity_date), group in df.groupby(["user_id", "activity_date"]):
        rows.append({
            "timestamp": pick_representative_timestamp(group).strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_id,
            "role": employee_roles.get(user_id, "Unknown"),
            "records_accessed": int(group["records_count"].sum()),
            "failed_logins": int(group["is_failed_login"].sum()),
            "action_type": "Download" if group["is_download"].any() else "View",
            "account_sensitivity": pick_representative_sensitivity(group),
            "ip_address": pick_representative_ip(group),
            "saved_ip": group.iloc[0]["saved_ip"],
        })
    result = pd.DataFrame(rows)
    return result.sort_values(["user_id", "timestamp"]).reset_index(drop=True)
 
 
def run(raw_log_path=RAW_LOG_PATH, employee_roles_path=EMPLOYEE_ROLES_PATH,
        employee_saved_ips_path=EMPLOYEE_SAVED_IPS_PATH, output_path=OUTPUT_PATH):
    employee_roles = load_json(employee_roles_path)
    employee_saved_ips = load_json(employee_saved_ips_path)
    raw = load_raw_logs(raw_log_path)
    tagged = tag_rows(raw, employee_saved_ips)
    result = aggregate(tagged, employee_roles)
    result.to_csv(output_path, index=False)
    return result, output_path
 
 
if __name__ == "__main__":
    result, path = run()
    print(f"--- Aggregated to {len(result)} rows - one per user ---")
    print(result.to_string(index=False))
    print(f"\nSaved to: {path}")