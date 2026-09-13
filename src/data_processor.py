import pandas as pd

def build_user_timelines(raw_df: pd.DataFrame) -> dict:
    """
    Mengelompokkan raw audit logs berdasarkan user_id dan menyusunnya
    menjadi kronologi aktivitas (User Activity Timeline).
    """
    user_timelines = {}
    
    if 'timestamp' in raw_df.columns:
        raw_df = raw_df.sort_values('timestamp')
        
    for user_id, group in raw_df.groupby('user_id'):
        role = group['role'].iloc[0] if 'role' in group.columns else 'Unknown'
        
        events = []
        for _, row in group.iterrows():
            event_str = (
                f"[{row.get('timestamp', 'N/A')}] "
                f"Action: {row.get('action_type', 'View')} | "
                f"Records: {row.get('records_accessed', 0)} | "
                f"Failed Logins: {row.get('failed_logins', 0)} | "
                f"Sensitivity: {row.get('account_sensitivity', 'Normal')} | "
                f"IP: {row.get('ip_address', 'N/A')} (Saved: {row.get('saved_ip', 'N/A')})"
            )
            events.append(event_str)
            
        user_timelines[user_id] = {
            "role": role,
            "timeline_text": "\n".join(events),
            "raw_events_count": len(group)
        }
        
    return user_timelines

def extract_summary_features(group_df: pd.DataFrame) -> dict:
    """
    Fitur agregasi ringkas untuk dievaluasi oleh 5-Rule Baseline Engine.
    """
    return {
        "user_id": group_df['user_id'].iloc[0],
        "role": group_df['role'].iloc[0],
        "total_records_accessed": group_df['records_accessed'].sum(),
        "total_failed_logins": group_df['failed_logins'].sum(),
        "accessed_vip": (group_df['account_sensitivity'] == 'Sensitive/VIP').any(),
        "has_unrecognized_ip": (group_df['ip_address'] != group_df['saved_ip']).any(),
        "has_after_hours": (group_df['is_after_hours'] == True).any() if 'is_after_hours' in group_df.columns else False
    }