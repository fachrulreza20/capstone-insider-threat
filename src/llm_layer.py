import json
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_user_timeline_with_llm(user_id: str, role: str, timeline_text: str, baseline_rules: str, baseline_risk: str) -> dict:
    """
    LLM Contextual Analysis: Membaca kronologi log mentah untuk menganalisis
    pola perilaku, kesesuaian peran, dan memberikan penjelasan berbasis bukti.
    """
    system_prompt = """
    You are an expert Security Operations Center (SOC) Analyst assisting in Insider Threat Hunting.
    Your objective is to evaluate chronological User Activity Timelines to detect suspicious behavioral patterns.

    Key Evaluation Guidelines:
    1. Sequence & Temporal Analysis: Check if actions follow a suspicious sequence (e.g., failed logins followed by VIP access or unusual data volume).
    2. Role Context: Evaluate if the accessed data and activity volume align with the user's operational role.
    3. Outcome Distinction: Differentiate between potential compromised credentials vs. suspicious insider activity.

    Important Framing Rules:
    - Do NOT state that a user has "malicious intent" or is a "bad person".
    - Frame findings as "Suspicious User / High-Risk Behavior Pattern" or "Consistent with Routine Activity".

    Return ONLY a valid JSON object with the following structure:
    {
      "llm_risk_level": "Low" | "Medium" | "High",
      "detected_pattern": "Short description of detected pattern (e.g., After-Hours Multi-Vector Access)",
      "explanation": "Concise step-by-step reasoning citing specific timeline evidence."
    }
    """

    user_prompt = f"""
    Please evaluate the following user activity profile:

    - User ID: {user_id}
    - Role: {role}
    - Rule-based Baseline Output: {baseline_risk} (Triggered Rules: {baseline_rules})

    User Activity Timeline (Chronological Audit Logs):
    {timeline_text}

    Analyze the timeline sequence and provide your contextual assessment in JSON format.
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        return json.loads(response.choices[0].message.content)

    except Exception as e:
        return {
            "llm_risk_level": baseline_risk,
            "detected_pattern": "API Error / Processing Failure",
            "explanation": f"Failed to perform LLM analysis: {str(e)}"
        }