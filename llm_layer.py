import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load Environment Variables (API Key)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set. Add it to your .env file or environment variables.")

client = OpenAI(api_key=api_key)

# Load Baseline
with open('role_baselines.json') as f:
    baselines = json.load(f)

def assess_risk_with_llm(user_id, role, timestamp, records_accessed, triggered_rules, base_risk):
    role_info = baselines.get(role, {})
    
    # Rancang Prompt Berbasis Konteks Bisnis
    prompt = f"""
    You are a Cybersecurity Analyst evaluating an internal insider threat alert for a bank.
    
    BUSINESS CONTEXT & BASELINE:
    - User Role: {role}
    - Expected Hours: {role_info.get('start_time')} to {role_info.get('end_time')}
    - Max Allowed Daily Access: {role_info.get('max_daily_records')} records
    
    AUDIT EVENT DETAILS:
    - User ID: {user_id}
    - Event Time: {timestamp}
    - Records Accessed: {records_accessed}
    - Rules Triggered: {triggered_rules}
    - Initial Rule-Based Risk: {base_risk}
    
    TASK:
    Analyze this incident considering the business context. 
    Provide your output in JSON format with two keys:
    1. "llm_risk_level": Must be "Low", "Medium", or "High"
    2. "explanation": A concise 1-2 sentence justification for your decision.
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

# Pengujian pada 1 sampel log
if __name__ == "__main__":
    test_result = assess_risk_with_llm(
        user_id="USR002",
        role="Teller",
        timestamp="2026-08-25 21:15:00",
        records_accessed=20,
        triggered_rules="Rule 1: Outside Working Hours",
        base_risk="Medium"
    )
    print("\n=== HASIL EVALUASI LLM LAYER ===")
    print(json.dumps(test_result, indent=2))