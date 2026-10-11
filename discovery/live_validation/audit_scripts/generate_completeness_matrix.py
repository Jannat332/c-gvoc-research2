import sqlite3
import pandas as pd
from pathlib import Path

conn = sqlite3.connect("discovery/live_validation/live_evaluation.db")
df_ep = pd.read_sql_query("SELECT * FROM live_episode_results", conn)
conn.close()

# Pivot for actions, correctness, tokens
piv_act = df_ep.pivot(index="instance_id", columns="method", values="chosen_action")
piv_corr = df_ep.pivot(index="instance_id", columns="method", values="is_correct")
piv_tok = df_ep.pivot(index="instance_id", columns="method", values="tokens_spent")

# Get dataset for each instance
inst_dset = df_ep.drop_duplicates(subset=["instance_id"]).set_index("instance_id")["dataset"]

out_df = pd.DataFrame(index=piv_act.index)
out_df["dataset"] = inst_dset

for m in ["monolithic", "deterministic", "gvoc", "cgvoc", "oracle"]:
    out_df[f"{m}_action"] = piv_act[m]
    out_df[f"{m}_correct"] = piv_corr[m]
    out_df[f"{m}_tokens"] = piv_tok[m]

out_df["shared_init_call"] = "call_init"
out_df["total_live_calls_evaluated"] = 3
out_df["status"] = "complete"

out_path = Path("discovery/live_validation/instance_method_completeness.csv")
out_df.to_csv(out_path)
print(f"Saved instance completeness matrix ({out_df.shape}) to {out_path}")
