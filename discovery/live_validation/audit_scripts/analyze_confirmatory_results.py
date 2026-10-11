import sqlite3
import pandas as pd
import numpy as np
from scipy import stats

conn = sqlite3.connect("discovery/live_validation/confirmatory_experiment/confirmatory_evaluation.db")
df = pd.read_sql_query("SELECT * FROM confirmatory_results", conn)
conn.close()

def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    spread = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, centre - spread), min(1.0, centre + spread))

def mcnemar_exact(y1, y2):
    n10 = np.sum((y1 == 1) & (y2 == 0))
    n01 = np.sum((y1 == 0) & (y2 == 1))
    n_disc = n10 + n01
    if n_disc == 0:
        return 1.0, n10, n01
    k = min(n10, n01)
    p_val = 2.0 * stats.binom.cdf(k, n_disc, 0.5)
    return min(1.0, p_val), n10, n01

print("="*90)
print("CONFIRMATORY EXPERIMENT: OVERALL PERFORMANCE ACROSS PREREGISTERED CONDITIONS (N = 20)")
print("="*90)

conditions = ["C1", "C2", "C3", "C4", "C5"]
cond_names = {
    "C1": "Full_Direct (O_full, conc, 60)",
    "C2": "Degraded_Direct (O_low, conc, 60)",
    "C3": "Degraded_Reasoning (O_low, conv, 256)",
    "C4": "Crop_Observation (O_crop, conc, 60)",
    "C5": "Full_Conversational_60 (O_full, conv, 60)"
}

summary_rows = []
for cid in conditions:
    sub = df[df["condition_id"] == cid]
    n = len(sub)
    k = sub["is_correct"].sum()
    acc = k / n
    ci_low, ci_high = wilson_ci(k, n)
    trunc_rate = (sub["finish_reason"] == "length").mean()
    m_compl = sub["completion_tokens"].mean()
    m_prompt = sub["prompt_tokens"].mean()
    m_total = sub["total_tokens"].mean()
    m_lat = sub["latency_sec"].mean()
    summary_rows.append({
        "ID": cid,
        "Name": cond_names[cid],
        "Acc": acc,
        "CI": f"[{ci_low*100:.1f}, {ci_high*100:.1f}]",
        "K/N": f"{k}/{n}",
        "Trunc%": f"{trunc_rate*100:.1f}%",
        "ComplTok": f"{m_compl:.1f}",
        "TotalTok": f"{m_total:.1f}",
        "Lat": f"{m_lat:.2f}s"
    })

sum_df = pd.DataFrame(summary_rows)
print(sum_df.to_string(index=False))

print("\n" + "="*90)
print("PER-DATASET STRATIFICATION (DOCVQA N=10, CHARTQA N=10)")
print("="*90)

for dset in ["docvqa", "chartqa"]:
    print(f"\n--- DATASET: {dset.upper()} (N=10) ---")
    for cid in conditions:
        sub = df[(df["dataset"] == dset) & (df["condition_id"] == cid)]
        n = len(sub)
        k = sub["is_correct"].sum()
        ci_low, ci_high = wilson_ci(k, n)
        trunc = (sub["finish_reason"] == "length").mean()
        mtok = sub["completion_tokens"].mean()
        print(f"  {cid:2s} ({cond_names[cid][:32]:32s}): Acc={k/n*100:.1f}% ({k}/{n}) [{ci_low*100:.1f}, {ci_high*100:.1f}], Trunc={trunc*100:.1f}%, ComplTok={mtok:.1f}")

print("\n" + "="*90)
print("PAIRED CONTRASTS & HYPOTHESIS TESTING (McNemar Exact Tests, N=20)")
print("="*90)

piv_corr = df.pivot(index="instance_id", columns="condition_id", values="is_correct")

# Contrast 1: Hypothesis 1 (Observation Crop C4 vs Degraded Reasoning C3)
p_val_h1, n10_h1, n01_h1 = mcnemar_exact(piv_corr["C4"].values, piv_corr["C3"].values)
print(f"Contrast 1 (Hypothesis 1): C4 (Crop_Observation) vs C3 (Degraded_Reasoning)")
print(f"  Accuracy: C4 = {piv_corr['C4'].mean()*100:.1f}% vs C3 = {piv_corr['C3'].mean()*100:.1f}%")
print(f"  Discordant: C4 correct & C3 incorrect = {n10_h1}, C4 incorrect & C3 correct = {n01_h1}")
print(f"  McNemar Exact p-value: {p_val_h1:.4f}")

# Contrast 2: Reasoning Scaling on Degraded Input (C3 vs C2)
p_val_c3_c2, n10_c3, n01_c3 = mcnemar_exact(piv_corr["C3"].values, piv_corr["C2"].values)
print(f"\nContrast 2 (Reasoning Scaling): C3 (Degraded_Reasoning) vs C2 (Degraded_Direct)")
print(f"  Accuracy: C3 = {piv_corr['C3'].mean()*100:.1f}% vs C2 = {piv_corr['C2'].mean()*100:.1f}%")
print(f"  Discordant: C3 correct & C2 incorrect = {n10_c3}, C3 incorrect & C2 correct = {n01_c3}")
print(f"  McNemar Exact p-value: {p_val_c3_c2:.4f}")

# Contrast 3: Degradation Impact (C1 vs C2)
p_val_c1_c2, n10_c1, n01_c1 = mcnemar_exact(piv_corr["C1"].values, piv_corr["C2"].values)
print(f"\nContrast 3 (Sensory Degradation): C1 (Full_Direct) vs C2 (Degraded_Direct)")
print(f"  Accuracy: C1 = {piv_corr['C1'].mean()*100:.1f}% vs C2 = {piv_corr['C2'].mean()*100:.1f}%")
print(f"  Discordant: C1 correct & C2 incorrect = {n10_c1}, C1 incorrect & C2 correct = {n01_c1}")
print(f"  McNemar Exact p-value: {p_val_c1_c2:.4f}")

# Contrast 4: Hypothesis 2 (Truncation Effect: C1 vs C5)
p_val_h2, n10_h2, n01_h2 = mcnemar_exact(piv_corr["C1"].values, piv_corr["C5"].values)
print(f"\nContrast 4 (Hypothesis 2: Truncation Ceiling): C1 (Full_Direct) vs C5 (Full_Conversational_60)")
print(f"  Accuracy: C1 = {piv_corr['C1'].mean()*100:.1f}% vs C5 = {piv_corr['C5'].mean()*100:.1f}%")
print(f"  Discordant: C1 correct & C5 incorrect = {n10_h2}, C1 incorrect & C5 correct = {n01_h2}")
print(f"  McNemar Exact p-value: {p_val_h2:.4f}")

print("\n" + "="*90)
print("INSTANCE-LEVEL OUTCOME MATRIX")
print("="*90)
piv_names = df.pivot(index="instance_id", columns="condition_id", values="response_text")
piv_fin = df.pivot(index="instance_id", columns="condition_id", values="finish_reason")

for inst_id in piv_corr.index:
    dset = df[df["instance_id"] == inst_id]["dataset"].iloc[0]
    c_scores = [str(piv_corr.loc[inst_id, cid]) for cid in conditions]
    c_fin = [piv_fin.loc[inst_id, cid] for cid in conditions]
    print(f"{inst_id} ({dset:7s}): Scores={'/'.join(c_scores)} | Finishes={'/'.join(c_fin)}")
