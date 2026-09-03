import os
import sys
import json
import pandas as pd
import streamlit as st
from datetime import datetime

# Add 'src' directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rule_engine import evaluate_log_entry
from llm_layer import assess_risk_with_llm

# Page Configuration
st.set_page_config(
    page_title="Insider Threat Detection System",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Business Context-Aware Insider Threat Detection System")
st.markdown("A lightweight hybrid model combining a 5-Rule Deterministic Engine with an LLM Contextual Layer (`gpt-4o-mini`).")

st.divider()

# Layout Split: Form on Left, Results on Right
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Input Employee Activity Log")
    
    user_id = st.text_input("User ID", value="USR001")
    role = st.selectbox("Organizational Role", ["Teller", "Customer Service", "Branch Manager"])
    
    log_time = st.time_input("Activity Time", value=datetime.strptime("20:30", "%H:%M").time())
    timestamp = f"2026-09-01 {log_time.strftime('%H:%M:%S')}"
    
    failed_logins = st.number_input("Failed Login Attempts", min_value=0, max_value=10, value=4)
    action_type = st.radio("Action Type", ["View", "Download"], horizontal=True, index=1)
    records_accessed = st.number_input("Number of Records Accessed", min_value=0, max_value=1000, value=120)
    
    account_sens_choice = st.checkbox("Accessing Sensitive / VIP Account?", value=True)
    account_sensitivity = "Sensitive/VIP" if account_sens_choice else "Normal"
    
    unrecognized_ip = st.checkbox("Accessing from Unrecognized / Foreign IP?", value=True)
    if unrecognized_ip:
        ip_address = "203.0.113.50"
        saved_ip = "192.168.1.10"
    else:
        ip_address = "192.168.1.10"
        saved_ip = "192.168.1.10"

    submit_button = st.button("🚀 Analyze Activity", type="primary", use_container_width=True)

with col2:
    st.subheader("🔍 Analysis Results")
    
    if submit_button:
        log_data = pd.Series({
            'scenario_id': 'DEMO_WEB',
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
        
        # Step 1: Rule Engine Evaluation
        triggered_rules, deterministic_risk = evaluate_log_entry(log_data)
        
        st.markdown("### ⚙️ Layer 1: Deterministic Rule Engine")
        
        r1 = "🔴 TRIGGERED" if any("Rule 1" in r for r in triggered_rules) else "🟢 CLEARED"
        r2 = "🔴 TRIGGERED" if any("Rule 2" in r for r in triggered_rules) else "🟢 CLEARED"
        r3 = "🔴 TRIGGERED" if any("Rule 3" in r for r in triggered_rules) else "🟢 CLEARED"
        r4 = "🔴 TRIGGERED" if any("Rule 4" in r for r in triggered_rules) else "🟢 CLEARED"
        r5 = "🔴 TRIGGERED" if any("Rule 5" in r for r in triggered_rules) else "🟢 CLEARED"
        
        st.text(f"Rule 1 (Outside Hours)      : {r1}")
        st.text(f"Rule 2 (Failed Logins >= 3) : {r2}")
        st.text(f"Rule 3 (Mass Download Limit): {r3}")
        st.text(f"Rule 4 (Sensitive/VIP Data) : {r4}")
        st.text(f"Rule 5 (Unrecognized IP)    : {r5}")
        
        st.info(f"**Baseline Risk Level:** {deterministic_risk.upper()} ({len(triggered_rules)}/5 Rules Triggered)")
        
        st.divider()
        
        # Step 2: LLM Assessment
        st.markdown("### 🤖 Layer 2: LLM Contextual Assessment (`gpt-4o-mini`)")
        with st.spinner("Evaluating business reasoning with AI..."):
            triggered_str = "; ".join(triggered_rules) if triggered_rules else "None"
            llm_response = assess_risk_with_llm(log_data, triggered_str, deterministic_risk)
            
            final_risk = llm_response.get("llm_risk_level", "Error").upper()
            explanation = llm_response.get("explanation", "N/A")
            
            if final_risk == "HIGH":
                st.error(f"**Final Risk Level: {final_risk}**")
            elif final_risk == "MEDIUM":
                st.warning(f"**Final Risk Level: {final_risk}**")
            else:
                st.success(f"**Final Risk Level: {final_risk}**")
                
            st.markdown(f"**Contextual Explanation:**\n{explanation}")
    else:
        st.info("Configure employee activity parameters on the left and click **Analyze Activity**.")