import os
import sys
import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Add 'src' directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rule_engine import evaluate_log_entry
from llm_layer import assess_risk_with_llm

# Set Page Config
st.set_page_config(
    page_title="Insider Threat Detection System",
    page_icon="🛡️",
    layout="wide"
)

# Page Title & Header
st.title("🛡️ Insider Threat Detection Dashboard")
st.markdown("This system evaluates employee activity logs for potential insider threats, providing both baseline risk detection and nuanced business context reasoning using a hybrid model (5-Rule Deterministic Engine + LLM Layer).")

# Tab Navigation (3 Tabs)
tab1, tab2, tab3 = st.tabs([
    "#1 🎯 Live Single Detection Demo", 
    "#2 📊 32-Scenario Evaluation Analytics",
    "#3 📁 Upload & Analyze Audit Logs"
])

# ==============================================================================
# TAB 1: LIVE SINGLE DETECTION DEMO
# ==============================================================================
with tab1:
    st.info("""
    **🎯 Objective & Purpose:** 
    Interactive single-event demonstration designed to showcase **how the system evaluates individual employee activities in real-time**. 
    It illustrates the two-layer detection process: first establishing a deterministic baseline via hardcoded security rules, and then using an LLM (`gpt-4o-mini`) to infer business context and intent.
    """)
    
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
        st.subheader("🔍 Real-time Detection Output")
        st.caption("The activity analysis is delivered in two distinct stages: **Layer 1 (Deterministic Rule Engine)** for baseline threshold checks, followed by **Layer 2 (LLM Contextual Assessment)** for business intent reasoning.")
        st.divider()
        
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
            
            # Step 1: Rule Engine
            triggered_rules, deterministic_risk = evaluate_log_entry(log_data)
            
            st.markdown("### ⚙️ Layer 1: Deterministic Rule Engine")
            
            r1 = "🔴 TRIGGERED" if any("Rule 1" in r for r in triggered_rules) else "🟢 CLEARED"
            r2 = "🔴 TRIGGERED" if any("Rule 2" in r for r in triggered_rules) else "🟢 CLEARED"
            r3 = "🔴 TRIGGERED" if any("Rule 3" in r for r in triggered_rules) else "🟢 CLEARED"
            r4 = "🔴 TRIGGERED" if any("Rule 4" in r for r in triggered_rules) else "🟢 CLEARED"
            r5 = "🔴 TRIGGERED" if any("Rule 5" in r for r in triggered_rules) else "🟢 CLEARED"
            
            st.text(f"Rule 1 (Outside Working Hours) : {r1}")
            st.text(f"Rule 2 (Failed Logins >= 3)    : {r2}")
            st.text(f"Rule 3 (Mass Data Download)    : {r3}")
            st.text(f"Rule 4 (Sensitive/VIP Access)  : {r4}")
            st.text(f"Rule 5 (Unrecognized IP)       : {r5}")
            
            st.info(f"**Deterministic Risk Level:** {deterministic_risk.upper()} ({len(triggered_rules)}/5 Rules Triggered)")
            st.divider()
            
            # Step 2: LLM Assessment
            st.markdown("### 🤖 Layer 2: LLM Contextual Assessment (`gpt-4o-mini`)")
            with st.spinner("Evaluating business context with AI..."):
                triggered_str = "; ".join(triggered_rules) if triggered_rules else "None"
                llm_response = assess_risk_with_llm(log_data, triggered_str, deterministic_risk)
                
                final_risk = llm_response.get("llm_risk_level", "Error").upper()
                explanation = llm_response.get("explanation", "N/A")
                
                if final_risk == "HIGH":
                    st.error(f"**Final Evaluated Risk Level: {final_risk}**")
                elif final_risk == "MEDIUM":
                    st.warning(f"**Final Evaluated Risk Level: {final_risk}**")
                else:
                    st.success(f"**Final Evaluated Risk Level: {final_risk}**")
                    
                st.markdown(f"**Reasoning Explanation:**\n{explanation}")
        else:
            st.info("Configure employee parameters on the left and click **Analyze Activity**.")

# ==============================================================================
# TAB 2: 32-SCENARIO EVALUATION ANALYTICS
# ==============================================================================
with tab2:
    st.info("""
    **📊 Objective & Purpose:** 
    Comprehensive evaluation summary presenting the **system-wide benchmark across all 32 full-factorial scenario combinations** ($2^5$ rule triggers). 
    This tab proves how the LLM layer adds value by resolving false negatives and contextualizing risk levels across different organizational roles (Teller, CS, Branch Manager).
    """)
    
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'experiment_results.csv')
    if os.path.exists(csv_path):
        df_results = pd.read_csv(csv_path)
        
        # 1. Summary Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Scenarios", len(df_results))
        m2.metric("High Risk Scenarios", len(df_results[df_results['LLM_Risk'] == 'High']))
        m3.metric("Medium Risk Scenarios", len(df_results[df_results['LLM_Risk'] == 'Medium']))
        m4.metric("Contextual Escalations", len(df_results[df_results['Override_Status'].str.contains('Overridden')]))
        
        st.divider()
        
        # 2. Detailed Scenario Dataset Table (DIATAS)
        st.markdown("### 📑 Detailed Scenario Dataset")
        st.dataframe(
            df_results,
            use_container_width=True,
            column_config={
                "Scenario_ID": st.column_config.TextColumn("Scenario ID", width="small"),
                "User_ID": st.column_config.TextColumn("User ID", width="small"),
                "Role": st.column_config.TextColumn("Role", width="small"),
                "Triggered_Count": st.column_config.NumberColumn("Rules Count", width="small"),
                "Triggered_Rules": st.column_config.TextColumn("Triggered Rules", width="medium"),
                "Deterministic_Risk": st.column_config.TextColumn("Base Risk", width="small"),
                "LLM_Risk": st.column_config.TextColumn("LLM Risk", width="small"),
                "Override_Status": st.column_config.TextColumn("Override Status", width="medium"),
                "LLM_Explanation": st.column_config.TextColumn(
                    "LLM Explanation",
                    width="large",
                )
            },
            hide_index=True
        )
        
        st.divider()
        
        # 3. Visual Analytics Charts (DIBAWAH)
        st.markdown("### 📊 Evaluation Visual Analytics")
        fig_web, axes = plt.subplots(1, 2, figsize=(12, 4.5))
        sns.set_theme(style="whitegrid")
        
        # Chart 1: Bar Plot Comparison
        risk_order = ['Low', 'Medium', 'High']
        det_counts = df_results['Deterministic_Risk'].value_counts().reindex(risk_order, fill_value=0)
        llm_counts = df_results['LLM_Risk'].value_counts().reindex(risk_order, fill_value=0)
        
        comp_df = pd.DataFrame({'Deterministic (Rule Engine)': det_counts, 'LLM (Contextual Layer)': llm_counts})
        comp_df.plot(kind='bar', ax=axes[0], color=['#3498db', '#e74c3c'], width=0.6)
        axes[0].set_title('Risk Level Shift: Deterministic vs LLM', fontweight='bold')
        axes[0].set_ylabel('Number of Scenarios')
        axes[0].set_xticklabels(risk_order, rotation=0)
        
        # Chart 2: Pie Chart Decision Impact
        override_counts = df_results['Override_Status'].value_counts()
        colors = ['#2ecc71' if 'Maintained' in x else '#e67e22' for x in override_counts.index]
        axes[1].pie(override_counts, labels=override_counts.index, autopct='%1.1f%%', startangle=140, colors=colors)
        axes[1].set_title('LLM Decision Impact', fontweight='bold')
        
        st.pyplot(fig_web)
        
    else:
        st.warning("`data/experiment_results.csv` not found. Please run `python src/run_32_scenarios.py` first.")

# ==============================================================================
# TAB 3: UPLOAD & ANALYZE AUDIT LOG FILES
# ==============================================================================
with tab3:
    st.info("""
    **📁 Objective & Purpose:** 
    Batch processing portal that allows security analysts to **upload custom audit log CSV files and execute risk evaluations**. 
    It provides flexibility to compare fast, low-cost **Deterministic Baseline Analysis** against full **LLM-assisted Contextual Assessment**.
    """)
    
    # Download Sample Data Section
    sample_csv_path = os.path.join(os.path.dirname(__file__), 'data', 'all_32_scenarios.csv')
    if os.path.exists(sample_csv_path):
        with open(sample_csv_path, "rb") as file:
            st.download_button(
                label="📥 Download Sample Audit Log Template (.csv)",
                data=file,
                file_name="sample_audit_log_template.csv",
                mime="text/csv",
                help="Click to download a pre-formatted sample CSV file to see expected columns and data structure."
            )
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            st.success(f"Successfully loaded `{uploaded_file.name}` with {len(uploaded_df)} log entries.")
            
            st.markdown("### 📑 Preview Uploaded Data")
            st.dataframe(uploaded_df.head(5), use_container_width=True)
            
            st.divider()
            
            # Action Buttons Row
            btn_col1, btn_col2 = st.columns(2)
            
            # Initialize Session State Dataframe for Upload Results
            if "processed_upload_df" not in st.session_state:
                st.session_state.processed_upload_df = None

            with btn_col1:
                run_rule_only = st.button("⚙️ Analyze via Rule Engine (Deterministic Baseline)", use_container_width=True, type="secondary")
            
            with btn_col2:
                run_llm_analysis = st.button("🤖 Analyze via LLM Contextual Assessment (OpenAI API)", use_container_width=True, type="primary")

            # ----------------------------------------------------
            # Execution: Rule Engine Only
            # ----------------------------------------------------
            if run_rule_only:
                results = []
                for idx, row in uploaded_df.iterrows():
                    triggered_rules, deterministic_risk = evaluate_log_entry(row)
                    results.append({
                        "Scenario_ID": row.get('scenario_id', f"LOG_{idx+1}"),
                        "User_ID": row.get('user_id', 'N/A'),
                        "Role": row.get('role', 'N/A'),
                        "Triggered_Rules": "; ".join(triggered_rules) if triggered_rules else "None",
                        "Deterministic_Risk": deterministic_risk
                    })
                st.session_state.processed_upload_df = pd.DataFrame(results)
                st.success("Rule Engine evaluation completed!")

            # ----------------------------------------------------
            # Execution: Rule Engine + LLM Layer
            # ----------------------------------------------------
            if run_llm_analysis:
                results = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, row in uploaded_df.iterrows():
                    status_text.text(f"Evaluating log {idx+1}/{len(uploaded_df)} with gpt-4o-mini...")
                    triggered_rules, deterministic_risk = evaluate_log_entry(row)
                    triggered_str = "; ".join(triggered_rules) if triggered_rules else "None"
                    
                    llm_resp = assess_risk_with_llm(row, triggered_str, deterministic_risk)
                    llm_risk = llm_resp.get("llm_risk_level", "Error")
                    explanation = llm_resp.get("explanation", "N/A")
                    
                    override_status = "Maintained"
                    if deterministic_risk != llm_risk and llm_risk != "Error":
                        override_status = f"Overridden ({deterministic_risk} -> {llm_risk})"
                    
                    results.append({
                        "Scenario_ID": row.get('scenario_id', f"LOG_{idx+1}"),
                        "User_ID": row.get('user_id', 'N/A'),
                        "Role": row.get('role', 'N/A'),
                        "Triggered_Rules": triggered_str,
                        "Deterministic_Risk": deterministic_risk,
                        "LLM_Risk": llm_risk,
                        "Override_Status": override_status,
                        "LLM_Explanation": explanation
                    })
                    progress_bar.progress((idx + 1) / len(uploaded_df))
                    
                status_text.empty()
                progress_bar.empty()
                st.session_state.processed_upload_df = pd.DataFrame(results)
                st.success("Full Hybrid (Rule Engine + LLM) evaluation completed!")

            # ----------------------------------------------------
            # Display Results Table
            # ----------------------------------------------------
            if st.session_state.processed_upload_df is not None:
                st.markdown("### 🔍 Analysis Results")
                
                cols_config = {
                    "Scenario_ID": st.column_config.TextColumn("ID", width="small"),
                    "User_ID": st.column_config.TextColumn("User ID", width="small"),
                    "Role": st.column_config.TextColumn("Role", width="small"),
                    "Triggered_Rules": st.column_config.TextColumn("Triggered Rules", width="medium"),
                    "Deterministic_Risk": st.column_config.TextColumn("Base Risk", width="small"),
                }
                
                # Dynamically include LLM columns if present
                if "LLM_Risk" in st.session_state.processed_upload_df.columns:
                    cols_config["LLM_Risk"] = st.column_config.TextColumn("LLM Risk", width="small")
                    cols_config["Override_Status"] = st.column_config.TextColumn("Override Status", width="medium")
                    cols_config["LLM_Explanation"] = st.column_config.TextColumn("LLM Explanation", width="large")

                st.dataframe(
                    st.session_state.processed_upload_df,
                    use_container_width=True,
                    column_config=cols_config,
                    hide_index=True
                )
                
        except Exception as e:
            st.error(f"Error processing CSV file: {str(e)}")
    else:
        st.info("Please upload a `.csv` audit log file (or download and test with the sample template above) to begin analysis.")