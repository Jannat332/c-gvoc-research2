import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect("discovery/live_validation/diagnostic_experiment/diagnostic_evaluation.db")
df = pd.read_sql_query("SELECT * FROM diagnostic_results", conn)
conn.close()

piv_corr = df.pivot(index="instance_id", columns="condition", values="is_correct")
piv_finish = df.pivot(index="instance_id", columns="condition", values="finish_reason")
piv_compl = df.pivot(index="instance_id", columns="condition", values="completion_tokens")
piv_ans = df.pivot(index="instance_id", columns="condition", values="response_text")
stypes = df.groupby("instance_id")["subset_type"].first()

print("="*80)
print("CONTROLLED DIAGNOSTIC EXPERIMENT: INSTANCE-BY-CONDITION TRANSITIONS")
print("="*80)

for inst_id in piv_corr.index:
    st = stypes[inst_id]
    r_corr = piv_corr.loc[inst_id]
    r_fin = piv_finish.loc[inst_id]
    r_cmp = piv_compl.loc[inst_id]
    print(f"\n[{inst_id}] ({st})")
    for cond in ["A", "B", "C", "D", "E"]:
        ans = piv_ans.loc[inst_id, cond].replace("\n", " ")[:50]
        print(f"  Cond {cond}: corr={r_corr[cond]}, finish={r_fin[cond]:6s}, tokens={r_cmp[cond]:3d} | resp='{ans}'")

print("\n" + "="*80)
print("AGGREGATE SUMMARY BY CONDITION")
print("="*80)

for cond in ["A", "B", "C", "D", "E"]:
    sub = df[df["condition"] == cond]
    n = len(sub)
    acc = sub["is_correct"].mean()
    trunc_rate = (sub["finish_reason"] == "length").mean()
    mean_tok = sub["completion_tokens"].mean()
    med_tok = sub["completion_tokens"].median()
    tot_tok = sub["total_tokens"].sum()
    mean_lat = sub["latency_sec"].mean()
    print(f"Condition {cond}: Acc={acc*100:.1f}% ({sub['is_correct'].sum()}/{n}), Trunc={trunc_rate*100:.1f}%, MeanTok={mean_tok:.1f}, MedTok={med_tok:.1f}, TotalTok={tot_tok}, Lat={mean_lat:.2f}s")

print("\n" + "="*80)
print("BREAKDOWN BY SUBSET TYPE")
print("="*80)

for st in ["harmful", "beneficial", "stable_correct"]:
    print(f"\n--- Subset: {st.upper()} (N={len(df[(df['subset_type'] == st) & (df['condition'] == 'A')])}) ---")
    for cond in ["A", "B", "C", "D", "E"]:
        sub = df[(df["subset_type"] == st) & (df["condition"] == cond)]
        acc = sub["is_correct"].mean()
        trunc = (sub["finish_reason"] == "length").mean()
        mtok = sub["completion_tokens"].mean()
        print(f"  Cond {cond}: Acc={acc*100:.1f}% ({sub['is_correct'].sum()}/{len(sub)}), Trunc={trunc*100:.1f}%, MeanTok={mtok:.1f}")

# Paired Differences vs Condition A (Direct)
print("\n" + "="*80)
print("PAIRED DIFFERENCES VS CONDITION A (DIRECT INFERENCE)")
print("="*80)

a_corr = piv_corr["A"]
for cond in ["B", "C", "D", "E"]:
    c_corr = piv_corr[cond]
    diff = c_corr - a_corr
    n_harm = (diff == -1).sum()
    n_resc = (diff == 1).sum()
    n_tie = (diff == 0).sum()
    print(f"Cond {cond} vs Cond A: Net Diff={diff.mean()*100:+.1f} points (Harmful={n_harm}, Rescued={n_resc}, Tied={n_tie})")
