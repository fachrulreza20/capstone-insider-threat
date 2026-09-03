import os
import json
import pandas as pd
from datetime import datetime

# Path acuan folder utama
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(BASE_DIR, 'config', 'role_baselines.json')
sample_log_path = os.path.join(BASE_DIR, 'data', 'sample_audit_logs.csv')

# Load baselines
with open(config_path, 'r') as f:
    baselines = json.load(f)

def evaluate_log_entry(row):
    """
    Evaluates an individual audit log entry against 5 deterministic security rules.
    """
    user_role = row['role']
    timestamp = datetime.strptime(str(row['timestamp']), '%Y-%m-%d %H:%M:%S')
    accessed_count = row['records_accessed']
    failed_logins = row['failed_logins']
    action_type = row['action_type']
    account_sens = row['account_sensitivity']
    ip_address = row['ip_address']
    saved_ip = row['saved_ip']
    
    role_config = baselines.get(user_role, {})
    rules_triggered = []
    
    # Rule 1: Outside Working Hours (09:00 - 17:00)
    log_time = timestamp.time()
    start_time = datetime.strptime("09:00", "%H:%M").time()
    end_time = datetime.strptime("17:00", "%H:%M").time()
    if log_time < start_time or log_time > end_time:
        rules_triggered.append("Rule 1: Outside Working Hours")
        
    # Rule 2: Repeated Failed Logins (>3)
    if failed_logins > 3:
        rules_triggered.append("Rule 2: Repeated Failed Logins (>3)")
        
    # Rule 3: Mass Data Download (>99 records for Manager, >0 for others)
    max_download = role_config.get('max_download_limit', 0)
    if action_type == "Download" and accessed_count > max_download:
        rules_triggered.append(f"Rule 3: Mass Data Download (>{max_download} records)")
        
    # Rule 4: Access to Sensitive / VIP Customer Accounts
    if account_sens in ["Sensitive/VIP", "HIGH-RISK"]:
        rules_triggered.append("Rule 4: Sensitive/VIP Account Access")
        
    # Rule 5: Unrecognized / Unsaved IP Location
    if ip_address != saved_ip:
        rules_triggered.append("Rule 5: Unrecognized IP Location")
        
    # Rule-Counting Risk Mapping (0-1: Low, 2-3: Medium, 4-5: High)
    count = len(rules_triggered)
    if count <= 1:
        base_risk = "Low"
    elif 2 <= count <= 3:
        base_risk = "Medium"
    else:
        base_risk = "High"
        
    return rules_triggered, base_risk

if __name__ == "__main__":
    if os.path.exists(sample_log_path):
        df = pd.read_csv(sample_log_path)
        results = []
        for index, row in df.iterrows():
            triggered, risk = evaluate_log_entry(row)
            results.append({
                "User ID": row['user_id'],
                "Role": row['role'],
                "Count": len(triggered),
                "Triggered Rules": "; ".join(triggered) if triggered else "None",
                "Base Risk": risk
            })
        print(pd.DataFrame(results))