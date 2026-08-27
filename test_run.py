import pandas as pd
import json

# Read Audit Log
df = pd.read_csv('sample_audit_logs.csv')
print("--- Data Log Audit ---")
print(df)

# Read Baseline
with open('role_baselines.json') as f:
    baselines = json.load(f)
print("\n--- Data Baseline ---")
print(baselines)