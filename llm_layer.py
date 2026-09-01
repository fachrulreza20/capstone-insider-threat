import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from rule_engine import evaluate_log_entry

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def assess_risk_with_llm(log_row, triggered_rules, base_risk):
    """
    Evaluates audit log data using OpenAI API (gpt-4o-mini) with business context reasoning.
    """
    prompt = f"""
    You are a Cybersecurity Analyst evaluating an internal insider threat alert for a bank.
    
    Audit Log Context:
    - User ID: {log_row['user_id']}
    - Role: {log_row['role']}
    - Timestamp: {log_row['timestamp']}
    - Action Type: {log_row['action_type']}
    - Records Accessed: {log_row['records_accessed']}
    - Failed Login Attempts: {log_row['failed_logins']}
    - Account Sensitivity: {log_row['account_sensitivity']}
    - Access IP: {log_row['ip_address']} (Saved IP: {log_row['saved_ip']})
    
    Deterministic Rule Engine Assessment:
    - Rules Triggered: {triggered_rules}
    - Rule-Engine Initial Risk Assessment: {base_risk}
    
    Role Baseline Guidelines:
    - Expected Working Hours: 09:00 to 17:00
    - Manager daily download limit: 99 records. Others are strictly prohibited from downloading.
    
    Task:
    Analyze the business context and behavioral patterns. Determine if the initial risk level should be maintained or adjusted (Low, Medium, High).
    Provide a concise explanation for your decision.
    
    Return ONLY a JSON object with this format:
    {{
      "llm_risk_level": "Low | Medium | High",
      "explanation": "<your concise analytical explanation>"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"llm_risk_level": "Error", "explanation": str(e)}

if __name__ == "__main__":
    df = pd.read_csv('sample_audit_logs.csv')
    
    # Test Evaluation on USR005 (High Risk Case)
    test_row = df[df['user_id'] == 'USR005'].iloc[0]
    triggered, risk = evaluate_log_entry(test_row)
    
    print("\n" + "="*80)
    print("                 LLM CONTEXTUAL EVALUATION OUTPUT                        ")
    print("="*80)
    print(f"Target User ID        : {test_row['user_id']} ({test_row['role']})")
    print(f"Triggered Rules Count : {len(triggered)}")
    print(f"Triggered Rules List  : {'; '.join(triggered)}")
    print(f"Deterministic Risk    : {risk}")
    print("-" * 80)
    
    result = assess_risk_with_llm(test_row, triggered, risk)
    
    print("LLM Evaluation Result :")
    print(json.dumps(result, indent=4))
    print("="*80 + "\n")