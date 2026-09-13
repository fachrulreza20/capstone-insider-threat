import streamlit as st
import pandas as pd

# Import modul dari folder src
from src.data_processor import build_user_timelines, extract_summary_features
from src.rule_engine import evaluate_log_entry  # Menyesuaikan fungsi di rule_engine.py Anda
from src.llm_layer import analyze_user_timeline_with_llm

st.set_page_config(page_title="Insider Threat Detection System", layout="wide")

st.title("🛡️ Hybrid Insider Threat Detection & Pattern Analysis System")
st.caption("Layer 1: Deterministic 5-Rule Baseline | Layer 2: LLM Timeline Behavioral Analysis")

tab1, tab2, tab3 = st.tabs([
    "1️⃣ Live Timeline Analyzer", 
    "2️⃣ Benchmark Analytics", 
    "3️⃣ Batch Raw Audit Logs Processor"
])

# ==========================================
# TAB 1: LIVE TIMELINE ANALYZER
# ==========================================
with tab1:
    st.subheader("Single User Activity Timeline Analysis")
    st.markdown("Analisis urutan kronologis aktivitas pengguna menggunakan kombinasi Baseline Rules dan LLM Contextual Layer.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("**User Profile Setup**")
        user_id = st.text_input("User ID", "USR001")
        role = st.selectbox("Employee Role", ["Teller", "Customer Service", "Manager", "IT Admin"])
        
        st.write("**Simulated Sequence Log Entry**")
        sample_timeline = st.text_area(
            "Paste Chronological Timeline",
            value="[09:00] Action: View | Records: 5 | IP: 192.168.1.10\n"
                  "[14:30] Action: View | Records: 10 | IP: 192.168.1.10\n"
                  "[20:15] Action: Download | Records: 85 | Sensitivity: VIP | Failed Logins: 3 | IP: 203.0.113.50",
            height=150
        )
        
        rule_triggered_str = "R1 (Outside Hours); R2 (Failed Logins); R3 (Mass Download); R4 (VIP Access); R5 (Foreign IP)"
        base_risk = "High"
        
        run_btn = st.button("Run Hybrid Analysis")

    with col2:
        if run_btn:
            st.markdown("### Analysis Results")
            st.info(f"**Baseline Rule Risk:** {base_risk} (Triggers: {rule_triggered_str})")
            
            with st.spinner("Analyzing timeline sequence via LLM Contextual Engine..."):
                llm_res = analyze_user_timeline_with_llm(
                    user_id=user_id,
                    role=role,
                    timeline_text=sample_timeline,
                    baseline_rules=rule_triggered_str,
                    baseline_risk=base_risk
                )
            
            st.success(f"**LLM Contextual Risk:** {llm_res.get('llm_risk_level')}")
            st.markdown(f"**Detected Behavioral Pattern:** `{llm_res.get('detected_pattern')}`")
            st.markdown(f"**Evidence Explanation:**\n{llm_res.get('explanation')}")

# ==========================================
# TAB 2: BENCHMARK ANALYTICS
# ==========================================
with tab2:
    st.subheader("32-Scenario Full Factorial Matrix & Benchmark")
    st.markdown("Menampilkan hasil komparasi deteksi 5-Rule Baseline vs LLM Contextual Assessment.")
    try:
        scenarios_df = pd.read_csv("data/ground_truth_scenarios.csv")
        st.dataframe(scenarios_df, use_container_width=True)
    except Exception as e:
        st.warning("File data/ground_truth_scenarios.csv belum tersedia.")

# ==========================================
# TAB 3: BATCH RAW LOGS PROCESSOR
# ==========================================
with tab3:
    st.subheader("Upload & Process Raw Audit Logs")
    uploaded_file = st.file_uploader("Upload Raw CSV Log File", type=["csv"])
    
    if uploaded_file is not None:
        raw_df = pd.read_csv(uploaded_file)
        st.write("Uploaded Raw Logs Preview:", raw_df.head(3))
        
        if st.button("Process Batch Timelines"):
            timelines = build_user_timelines(raw_df)
            results = []
            
            progress_bar = st.progress(0)
            total_users = len(timelines)
            
            for idx, (u_id, u_data) in enumerate(timelines.items()):
                user_raw_df = raw_df[raw_df['user_id'] == u_id]
                features = extract_summary_features(user_raw_df)
                
                # Rule Engine Assessment
                triggered, base_risk = evaluate_log_entry(features)
                
                # LLM Timeline Assessment
                llm_out = analyze_user_timeline_with_llm(
                    user_id=u_id,
                    role=u_data['role'],
                    timeline_text=u_data['timeline_text'],
                    baseline_rules="; ".join(triggered) if triggered else "None",
                    baseline_risk=base_risk
                )
                
                results.append({
                    "User ID": u_id,
                    "Role": u_data['role'],
                    "Baseline Risk": base_risk,
                    "LLM Risk": llm_out.get('llm_risk_level'),
                    "Detected Pattern": llm_out.get('detected_pattern'),
                    "Evidence Reasoning": llm_out.get('explanation')
                })
                
                progress_bar.progress((idx + 1) / total_users)
                
            res_df = pd.DataFrame(results)
            st.dataframe(res_df, use_container_width=True)
            
            st.download_button(
                "Download Audit Results CSV",
                data=res_df.to_csv(index=False),
                file_name="hybrid_audit_report.csv",
                mime="text/csv"
            )