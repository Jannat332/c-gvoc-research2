import sqlite3
import pandas as pd
import json

conn = sqlite3.connect("discovery/live_validation/live_evaluation.db")
df_ep = pd.read_sql_query("SELECT * FROM live_episode_results WHERE dataset = 'chartqa'", conn)
df_calls = pd.read_sql_query("SELECT * FROM live_api_calls WHERE dataset = 'chartqa'", conn)
conn.close()

# Identify harmful flips for cgvoc on ChartQA (monolithic was 1, cgvoc was 0)
piv_corr = df_ep.pivot(index="instance_id", columns="method", values="is_correct")
piv_act = df_ep.pivot(index="instance_id", columns="method", values="chosen_action")
piv_ans = df_ep.pivot(index="instance_id", columns="method", values="final_answer")

cgvoc_harmful = piv_corr[(piv_corr["monolithic"] == 1) & (piv_corr["cgvoc"] == 0)].index.tolist()
print(f"ChartQA instances where C-GVoC caused harmful flip: {len(cgvoc_harmful)}")
print("Instance IDs:", cgvoc_harmful)

for inst_id in cgvoc_harmful:
    print(f"\n=======================================================")
    print(f"CASE STUDY: {inst_id}")
    print(f"=======================================================")
    inst_ep = df_ep[df_ep["instance_id"] == inst_id]
    query = inst_ep["query"].iloc[0]
    gt = inst_ep["ground_truth"].iloc[0]
    print(f"Query: {query}")
    print(f"Ground Truth: {gt}")
    
    # Calls for this instance
    calls = df_calls[df_calls["instance_id"] == inst_id].sort_values("timestamp")
    for _, c in calls.iterrows():
        print(f"\n  Call Role: {c['call_role']} | Tokens: {c['total_tokens']}")
        print(f"  Prompt: {c['prompt_text'][:120]}...")
        print(f"  Response: '{c['response_text']}'")
        
    print(f"\n  Method Outcomes:")
    print(f"    Monolithic: action={piv_act.loc[inst_id, 'monolithic']}, corr={piv_corr.loc[inst_id, 'monolithic']}, ans='{piv_ans.loc[inst_id, 'monolithic']}'")
    print(f"    C-GVoC:     action={piv_act.loc[inst_id, 'cgvoc']}, corr={piv_corr.loc[inst_id, 'cgvoc']}, ans='{piv_ans.loc[inst_id, 'cgvoc']}'")
    print(f"    GVoC:       action={piv_act.loc[inst_id, 'gvoc']}, corr={piv_corr.loc[inst_id, 'gvoc']}, ans='{piv_ans.loc[inst_id, 'gvoc']}'")
    print(f"    Oracle:     action={piv_act.loc[inst_id, 'oracle']}, corr={piv_corr.loc[inst_id, 'oracle']}, ans='{piv_ans.loc[inst_id, 'oracle']}'")
