import pandas as pd
import json
from datetime import datetime

# Load configuration baselines and audit log dataset
with open('role_baselines.json') as f:
    baselines = json.load(f)

df = pd.read_csv('sample_audit_logs.csv')

def evaluate_log_entry(row):
    """
    Evaluates an individual audit log entry against 5 deterministic security rules.
    Returns the list of triggered rules and the calculated baseline risk level.
    """
    user_role = row['role']
    timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
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
        
    # Rule 3: Mass Data Download (>99 records for Manager)
    max_download = role_config.get('max_download_limit', 0)
    if action_type == "Download" and accessed_count > max_download:
        rules_triggered.append(f"Rule 3: Mass Data Download (>{max_download} records)")
        
    # Rule 4: Access to Sensitive / VIP Customer Accounts
    if account_sens in ["Sensitive/VIP", "HIGH-RISK"]:
        rules_triggered.append("Rule 4: Sensitive/VIP Account Access")
        
    # Rule 5: Unrecognized / Unsaved IP Location
    if ip_address != saved_ip:
        rules_triggered.append("Rule 5: Unrecognized IP Location")
        
    # Deterministic Risk Mapping (Rule-Counting Thresholds)
    # 0-1 rules: Low | 2-3 rules: Medium | 4-5 rules: High
    count = len(rules_triggered)
    if count <= 1:
        base_risk = "Low"
    elif 2 <= count <= 3:
        base_risk = "Medium"
    else:
        base_risk = "High"
        
    return rules_triggered, base_risk

# Execute Evaluation
if __name__ == "__main__":
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

    results_df = pd.DataFrame(results)
    
    # Clean terminal output formatting
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    print("\n" + "="*80)
    print("      DETERMINISTIC RULE ENGINE ASSESSMENT RESULTS (5-RULE SYSTEM)      ")
    print("="*80)
    print(results_df.to_string(index=False))
    print("="*80 + "\n")