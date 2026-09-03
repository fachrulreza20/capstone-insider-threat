import os
import sys
import pandas as pd

# Add 'src' directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rule_engine import evaluate_log_entry
from llm_layer import assess_risk_with_llm

def get_user_input():
    print("\n" + "="*50)
    print("      INSIDER THREAT DETECTION SYSTEM (DEMO)      ")
    print("="*50)
    print("Please input the employee activity details:\n")
    
    user_id = input("User ID [e.g. USR001]: ").strip() or "USR001"
    
    print("\nSelect Role:")
    print("1. Teller")
    print("2. Customer Service")
    print("3. Branch Manager")
    role_choice = input("Choice (1-3) [default: 1]: ").strip()
    role_map = {"1": "Teller", "2": "Customer Service", "3": "Branch Manager"}
    role = role_map.get(role_choice, "Teller")
    
    login_time = input("\nLogin Time (HH:MM) [e.g. 20:30]: ").strip() or "20:30"
    timestamp = f"2026-09-01 {login_time}:00"
    
    try:
        failed_logins = int(input("Failed login attempts [e.g. 4]: ").strip() or "4")
    except ValueError:
        failed_logins = 4
        
    print("\nAction Type:")
    print("1. View")
    print("2. Download")
    action_choice = input("Choice (1-2) [default: 2]: ").strip()
    action_type = "Download" if action_choice == "2" else "View"
    
    try:
        records_accessed = int(input("\nNumber of records accessed [e.g. 120]: ").strip() or "120")
    except ValueError:
        records_accessed = 120
        
    sensitive_input = input("\nAccessing Sensitive/VIP data? (y/n) [default: y]: ").strip().lower()
    account_sensitivity = "Sensitive/VIP" if sensitive_input in ['y', 'yes', ''] else "Normal"
    
    ip_input = input("\nIs IP address recognized/saved? (y/n) [default: n]: ").strip().lower()
    if ip_input in ['n', 'no', '']:
        ip_address = "203.0.113.50"
        saved_ip = "192.168.1.10"
    else:
        ip_address = "192.168.1.10"
        saved_ip = "192.168.1.10"
        
    # Construct Pandas Series matching audit log schema
    log_data = pd.Series({
        'scenario_id': 'DEMO_SINGLE',
        'timestamp': timestamp,
        'user_id': user_id,
        'role': role,
        'records_accessed': records_accessed,
        'failed_logins': failed_logins,
        'action_type': action_type,
        'account_sensitivity': account_sensitivity,
        'ip_address': ip_address,
        'saved_ip': saved_ip
    })
    
    return log_data

def main():
    log_data = get_user_input()
    
    # ----------------------------------------------------
    # STEP 1: DETERMINISTIC RULE ENGINE EVALUATION
    # ----------------------------------------------------
    triggered_rules, deterministic_risk = evaluate_log_entry(log_data)
    triggered_count = len(triggered_rules)
    triggered_str = "; ".join(triggered_rules) if triggered_rules else "None"
    
    print("\n" + "-"*50)
    print("DETERMINISTIC RULE ENGINE")
    print("-"*50)
    
    # Status display for 5 rules
    r1_status = "TRIGGERED" if any("Rule 1" in r for r in triggered_rules) else "CLEARED"
    r2_status = "TRIGGERED" if any("Rule 2" in r for r in triggered_rules) else "CLEARED"
    r3_status = "TRIGGERED" if any("Rule 3" in r for r in triggered_rules) else "CLEARED"
    r4_status = "TRIGGERED" if any("Rule 4" in r for r in triggered_rules) else "CLEARED"
    r5_status = "TRIGGERED" if any("Rule 5" in r for r in triggered_rules) else "CLEARED"
    
    print(f"R1 Outside working hours       : {r1_status}")
    print(f"R2 Repeated failed login       : {r2_status}")
    print(f"R3 Mass data download          : {r3_status}")
    print(f"R4 Sensitive/VIP access        : {r4_status}")
    print(f"R5 Unrecognized IP             : {r5_status}")
    print(f"\nTriggered Rules: {triggered_count}/5")
    print(f"Initial Risk: {deterministic_risk.upper()}")
    
    # ----------------------------------------------------
    # STEP 2: LLM CONTEXTUAL ASSESSMENT
    # ----------------------------------------------------
    print("\n" + "-"*50)
    print("LLM CONTEXTUAL ASSESSMENT")
    print("-"*50)
    print("Evaluating business context with gpt-4o-mini...")
    
    llm_response = assess_risk_with_llm(log_data, triggered_str, deterministic_risk)
    
    final_risk = llm_response.get("llm_risk_level", "Error").upper()
    explanation = llm_response.get("explanation", "N/A")
    
    print(f"\nFinal Risk: {final_risk}")
    print(f"\nExplanation:\n{explanation}")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()