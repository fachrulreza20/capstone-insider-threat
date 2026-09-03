import os
import sys
import time
import pandas as pd

# Add 'src' directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rule_engine import evaluate_log_entry
from llm_layer import assess_risk_with_llm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scenarios_path = os.path.join(BASE_DIR, 'data', 'all_32_scenarios.csv')
output_path = os.path.join(BASE_DIR, 'data', 'experiment_results.csv')

def run_bulk_evaluation():
    print("\n" + "="*80)
    print("      STARTING BULK EVALUATION OF ALL 32 RULE-TRIGGER COMBINATIONS      ")
    print("="*80)
    
    scenarios_df = pd.read_csv(scenarios_path)
    results = []
    
    total_start_time = time.time()
    
    for idx, row in scenarios_df.iterrows():
        scenario_id = row['scenario_id']
        print(f"[*] Processing Scenario {scenario_id} ({idx+1}/32) for Role: {row['role']}...")
        
        # Step 1: Run Deterministic Rule Engine
        triggered_rules, deterministic_risk = evaluate_log_entry(row)
        triggered_count = len(triggered_rules)
        triggered_str = "; ".join(triggered_rules) if triggered_rules else "None"
        
        # Step 2: Run LLM Contextual Assessment Layer
        llm_response = assess_risk_with_llm(row, triggered_str, deterministic_risk)
        
        llm_risk = llm_response.get("llm_risk_level", "Error")
        llm_explanation = llm_response.get("explanation", "N/A")
        
        override_status = "Maintained"
        if deterministic_risk != llm_risk and llm_risk != "Error":
            override_status = f"Overridden ({deterministic_risk} -> {llm_risk})"
            
        results.append({
            "Scenario_ID": scenario_id,
            "User_ID": row['user_id'],
            "Role": row['role'],
            "Triggered_Count": triggered_count,
            "Triggered_Rules": triggered_str,
            "Deterministic_Risk": deterministic_risk,
            "LLM_Risk": llm_risk,
            "Override_Status": override_status,
            "LLM_Explanation": llm_explanation
        })
        
    total_duration = round(time.time() - total_start_time, 2)
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_path, index=False)
    
    print("="*80)
    print(f"[SUCCESS] Evaluated 32 scenarios across all roles in {total_duration} seconds.")
    print(f"[OUTPUT] Updated results saved to '{output_path}'.")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_bulk_evaluation()