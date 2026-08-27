import pandas as pd
import json
from datetime import datetime

# Load the baseline configuration and audit log data
with open('role_baselines.json') as f:
    baselines = json.load(f)

df = pd.read_csv('sample_audit_logs.csv')

def evaluate_log_entry(row):
    user_role = row['role']
    timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
    accessed_count = row['records_accessed']
    
    # Get the baseline configuration for the user's role
    role_config = baselines.get(user_role)
    if not role_config:
        return "Unknown Role", "Low"
    
    start_time = datetime.strptime(role_config['start_time'], '%H:%M').time()
    end_time = datetime.strptime(role_config['end_time'], '%H:%M').time()
    max_records = role_config['max_daily_records']
    
    rules_triggered = []
    
    # Check Rule 1: Outside Working Hours
    log_time = timestamp.time()
    if log_time < start_time or log_time > end_time:
        rules_triggered.append("Rule 1: Outside Working Hours")
        
    # Check Rule 2: Excessive Records Accessed
    if accessed_count > max_records:
        rules_triggered.append("Rule 2: Excessive Record Access")
        
    # Deterministic Risk Mapping
    if len(rules_triggered) == 0:
        risk_level = "Low"
    elif len(rules_triggered) == 1:
        risk_level = "Medium"
    else:
        risk_level = "High"
        
    return rules_triggered, risk_level

# Run the evaluation across the dataframe
results = []
for index, row in df.iterrows():
    triggered, risk = evaluate_log_entry(row)
    results.append({
        "user_id": row['user_id'],
        "role": row['role'],
        "triggered_rules": triggered,
        "base_risk": risk
    })

results_df = pd.DataFrame(results)
print("--- Rule Engine Evaluation Results ---")
print(results_df)