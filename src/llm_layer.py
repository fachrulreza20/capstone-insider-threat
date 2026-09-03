import os
import json
from openai import OpenAI

def get_openai_client():
    """
    Safely retrieves the OpenAI API key from environment variables or Streamlit Secrets.
    """
    # 1. Try fetching from Streamlit secrets (for Streamlit Cloud)
    try:
        import streamlit as st
        if "OPENAI_API_KEY" in st.secrets:
            return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except Exception:
        pass

    # 2. Try fetching from local .env environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return OpenAI(api_key=api_key)

    return None

def assess_risk_with_llm(log_entry, triggered_rules_str, deterministic_risk):
    """
    Evaluates business context using OpenAI gpt-4o-mini model.
    """
    client = get_openai_client()
    
    if not client:
        return {
            "llm_risk_level": deterministic_risk,
            "explanation": "OpenAI API Key is missing. Please configure OPENAI_API_KEY in Streamlit Secrets or .env file."
        }

    # Construct System Prompt
    system_prompt = (
        "You are an expert Cybersecurity SOC Analyst evaluating insider threats in a bank. "
        "Analyze the provided user log and deterministic rule triggers. "
        "Determine if the baseline risk should be maintained or escalated/overridden based on business context. "
        "Return ONLY a JSON object with keys: 'llm_risk_level' (Low, Medium, High) and 'explanation' (2-3 clear sentences)."
    )

    user_prompt = f"""
    Employee Log:
    - User ID: {log_entry['user_id']}
    - Role: {log_entry['role']}
    - Time: {log_entry['timestamp']}
    - Action: {log_entry['action_type']} ({log_entry['records_accessed']} records)
    - Failed Logins: {log_entry['failed_logins']}
    - Account Sensitivity: {log_entry['account_sensitivity']}
    - IP Match: {'Yes' if log_entry['ip_address'] == log_entry['saved_ip'] else 'No'}

    Deterministic Layer Output:
    - Triggered Rules: {triggered_rules_str}
    - Baseline Risk: {deterministic_risk}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "llm_risk_level": deterministic_risk,
            "explanation": f"API Error encountered: {str(e)}"
        }