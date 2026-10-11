import sqlite3
import pandas as pd

conn = sqlite3.connect("discovery/live_validation/live_evaluation.db")
df_ep = pd.read_sql_query("SELECT * FROM live_episode_results", conn)
df_calls = pd.read_sql_query("SELECT * FROM live_api_calls", conn)
conn.close()

piv_corr = df_ep.pivot(index="instance_id", columns="method", values="is_correct")
piv_act = df_ep.pivot(index="instance_id", columns="method", values="chosen_action")

# Instances where monolithic is correct (1) but either GVoC or C-GVoC is incorrect (0)
harmful_insts = piv_corr[(piv_corr["monolithic"] == 1) & ((piv_corr["gvoc"] == 0) | (piv_corr["cgvoc"] == 0))].index.tolist()
print(f"Total harmful instances (monolithic=1, GVoC or C-GVoC=0): {len(harmful_insts)}")

for inst_id in harmful_insts:
    ep = df_ep[df_ep["instance_id"] == inst_id]
    calls = df_calls[df_calls["instance_id"] == inst_id].sort_values("timestamp")
    q = ep["query"].iloc[0]
    gt = ep["ground_truth"].iloc[0]
    dset = ep["dataset"].iloc[0]
    m_act = piv_act.loc[inst_id, "monolithic"]
    g_act = piv_act.loc[inst_id, "gvoc"]
    cg_act = piv_act.loc[inst_id, "cgvoc"]
    print(f"\n--- {inst_id} ({dset}) ---")
    print(f"Q: {q}")
    print(f"GT: {gt}")
    print(f"Monolithic: act={m_act}, corr={piv_corr.loc[inst_id, 'monolithic']}")
    print(f"GVoC:       act={g_act}, corr={piv_corr.loc[inst_id, 'gvoc']}")
    print(f"C-GVoC:     act={cg_act}, corr={piv_corr.loc[inst_id, 'cgvoc']}")
    for _, c in calls.iterrows():
        print(f"  [{c['call_role']}]: prompt_tok={c['prompt_tokens']}, compl_tok={c['completion_tokens']}, text={repr(c['response_text'])}")
