import sqlite3
import pandas as pd
import json

conn = sqlite3.connect("discovery/live_validation/live_evaluation.db")
df_ep = pd.read_sql_query("SELECT * FROM live_episode_results WHERE dataset = 'chartqa'", conn)
df_calls = pd.read_sql_query("SELECT * FROM live_api_calls WHERE dataset = 'chartqa'", conn)
conn.close()

target_ids = ['chartqa_001', 'chartqa_002', 'chartqa_009', 'chartqa_011', 'chartqa_014', 'chartqa_022', 'chartqa_027', 'chartqa_030', 'chartqa_039', 'chartqa_041']

out = {}
for tid in target_ids:
    ep_sub = df_ep[df_ep['instance_id'] == tid]
    calls_sub = df_calls[df_calls['instance_id'] == tid].sort_values('timestamp')
    out[tid] = {
        'query': ep_sub['query'].iloc[0],
        'ground_truth': ep_sub['ground_truth'].iloc[0],
        'methods': {row['method']: {'action': row['chosen_action'], 'correct': int(row['is_correct']), 'answer': row['final_answer']} for _, row in ep_sub.iterrows()},
        'calls': [{'role': c['call_role'], 'prompt': c['prompt_text'], 'response': c['response_text'], 'tokens': int(c['total_tokens']), 'image_path': c['image_path']} for _, c in calls_sub.iterrows()]
    }

with open("discovery/live_validation/audit_scripts/chartqa_harmful_details.json", "w") as f:
    json.dump(out, f, indent=2)
print("Saved chartqa_harmful_details.json successfully")
