import os
import json
import pandas as pd
from datetime import datetime

# Define base directory path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(BASE_DIR, 'config', 'role_baselines.json')
sample_log_path = os.path.join(BASE_DIR, 'data', 'sample_audit_logs.csv')

# Load role baselines dynamic configuration
with open(config_path, 'r') as f:
    baselines = json.load(f)

def evaluate_log_entry(row):
    """
    Evaluates an individual audit log entry against 5 deterministic security rules.
    Dynamically loads threshold parameters from role_baselines.json.
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
    
    # Rule 1: Outside Working Hours (Dynamic lookup from JSON baseline)
    log_time = timestamp.time()
    start_str = role_config.get('start_time', '09:00')
    end_str = role_config.get('end_time', '17:00')
    start_time = datetime.strptime(start_str, "%H:%M").time()
    end_time = datetime.strptime(end_str, "%H:%M").time()
    
    if log_time < start_time or log_time > end_time:
        rules_triggered.append(f"Rule 1: Outside Working Hours ({start_str}-{end_str})")
        
    # Rule 2: Repeated Failed Logins (>= 3 attempts)
    if failed_logins >= 3:
        rules_triggered.append("Rule 2: Repeated Failed Logins (>= 3)")
        
    # Rule 3: Mass Data Download (Exceeds role download limit)
    max_download = role_config.get('max_download_limit', 0)
    if action_type == "Download" and accessed_count > max_download:
        rules_triggered.append(f"Rule 3: Mass Data Download (>{max_download} limit)")
        
    # Rule 4: Access to Sensitive / VIP Customer Accounts
    if account_sens in ["Sensitive/VIP", "HIGH-RISK"]:
        rules_triggered.append("Rule 4: Sensitive/VIP Account Access")
        
    # Rule 5: Unrecognized / Unsaved IP Location
    if ip_address != saved_ip:
        rules_triggered.append("Rule 5: Unrecognized IP Location")
        
    # Deterministic Risk Mapping (0-1: Low, 2-3: Medium, 4-5: High)
    count = len(rules_triggered)
    if count <= 1:
        base_risk = "Low"
    elif 2 <= count <= 3:
        base_risk = "Medium"
    else:
        base_risk = "High"
        
    return rules_triggered, base_risk