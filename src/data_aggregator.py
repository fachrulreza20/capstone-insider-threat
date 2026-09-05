import pandas as pd

def aggregate_user_logs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates raw audit log entries by user_id and scenario_id so that 
    accumulated metrics (e.g., total downloads, cumulative failed logins) 
    can be evaluated correctly by the 5-rule engine.
    """
    # If data is already aggregated (has unique scenario_ids or explicitly aggregated), return directly
    if 'is_aggregated' in df.columns or len(df) == df['user_id'].nunique():
        return df

    aggregated_results = []
    
    # Determine grouping key
    group_cols = [c for c in ['scenario_id', 'user_id', 'role'] if c in df.columns]
    if not group_cols:
        group_cols = ['user_id'] if 'user_id' in df.columns else df.index

    for _, group in df.groupby(group_cols):
        # 1. Total records accessed (cumulative sum)
        total_records = group['records_accessed'].sum() if 'records_accessed' in group.columns else 0
        
        # 2. Total failed logins (cumulative sum)
        total_failed_logins = group['failed_logins'].sum() if 'failed_logins' in group.columns else 0
        
        # 3. Action type (If any row has 'Download', aggregate action becomes 'Download')
        has_download = "Download" in group['action_type'].values if 'action_type' in group.columns else False
        action_type = "Download" if has_download else "View"
        
        # 4. Account Sensitivity (If accessed any VIP account, mark as Sensitive/VIP)
        has_vip = "Sensitive/VIP" in group['account_sensitivity'].values if 'account_sensitivity' in group.columns else False
        account_sensitivity = "Sensitive/VIP" if has_vip else "Normal"
        
        # 5. IP Address Check (If any transaction came from foreign IP, flag foreign IP)
        ip_mismatch = any(group['ip_address'] != group['saved_ip']) if ('ip_address' in group.columns and 'saved_ip' in group.columns) else False
        ip_addr = group['ip_address'].iloc[-1] if 'ip_address' in group.columns else "192.168.1.10"
        saved_ip = group['saved_ip'].iloc[-1] if 'saved_ip' in group.columns else "192.168.1.10"
        if ip_mismatch:
            ip_addr = "203.0.113.50"  # Set to unrecognized IP trigger
            
        agg_row = {
            'scenario_id': group['scenario_id'].iloc[0] if 'scenario_id' in group.columns else 'AGG_LOG',
            'timestamp': group['timestamp'].iloc[-1] if 'timestamp' in group.columns else '2026-09-01 17:00:00',
            'user_id': group['user_id'].iloc[0] if 'user_id' in group.columns else 'USR_UNKNOWN',
            'role': group['role'].iloc[0] if 'role' in group.columns else 'Teller',
            'records_accessed': total_records,
            'failed_logins': total_failed_logins,
            'action_type': action_type,
            'account_sensitivity': account_sensitivity,
            'ip_address': ip_addr,
            'saved_ip': saved_ip
        }
        aggregated_results.append(agg_row)
        
    return pd.DataFrame(aggregated_results)