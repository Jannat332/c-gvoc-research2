import sqlite3
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

# Connect to database
conn = sqlite3.connect("discovery/live_validation/live_evaluation.db")
df_ep = pd.read_sql_query("SELECT * FROM live_episode_results", conn)
df_calls = pd.read_sql_query("SELECT * FROM live_api_calls", conn)
conn.close()

# Pivot episode tables by instance
piv_corr = df_ep.pivot(index="instance_id", columns="method", values="is_correct")
piv_tok = df_ep.pivot(index="instance_id", columns="method", values="tokens_spent")
piv_act = df_ep.pivot(index="instance_id", columns="method", values="chosen_action")
inst_dset = df_ep.drop_duplicates(subset=["instance_id"]).set_index("instance_id")["dataset"]

methods = ["monolithic", "deterministic", "gvoc", "cgvoc", "oracle"]
mono_corr = piv_corr["monolithic"].values
mono_tok = piv_tok["monolithic"].values
n_total = len(mono_corr)

# Formula for normalized regret
# Regret_i = max(0, Oracle_acc_i - Acc_i) + 0.05 * max(0, Tokens_i - Oracle_tok_i) / 6000
oracle_corr = piv_corr["oracle"].values
oracle_tok = piv_tok["oracle"].values

def compute_metrics_for_subset(idx_filter=None, name="Overall"):
    rows = []
    sub_corr = piv_corr.loc[idx_filter] if idx_filter is not None else piv_corr
    sub_tok = piv_tok.loc[idx_filter] if idx_filter is not None else piv_tok
    sub_act = piv_act.loc[idx_filter] if idx_filter is not None else piv_act
    sub_oracle_c = sub_corr["oracle"].values
    sub_oracle_t = sub_tok["oracle"].values
    sub_mono_c = sub_corr["monolithic"].values
    sub_mono_t = sub_tok["monolithic"].values
    n = len(sub_corr)

    for m in methods:
        c_vals = sub_corr[m].values
        t_vals = sub_tok[m].values
        a_vals = sub_act[m].values

        acc = np.mean(c_vals)
        # Wilson score interval for binomial proportion
        z = 1.95996
        p_hat = np.mean(c_vals)
        denom = 1 + (z**2) / n
        center = (p_hat + (z**2) / (2 * n)) / denom
        spread = (z * np.sqrt((p_hat * (1 - p_hat)) / n + (z**2) / (4 * n**2))) / denom
        ci_low = max(0.0, float(center - spread))
        ci_high = min(1.0, float(center + spread))

        # Discordant pairs vs monolithic
        # n10: monolithic=1, method=0 (harmful flip)
        # n01: monolithic=0, method=1 (beneficial flip)
        # n11: both=1, n00: both=0
        n10 = int(np.sum((sub_mono_c == 1) & (c_vals == 0)))
        n01 = int(np.sum((sub_mono_c == 0) & (c_vals == 1)))
        n11 = int(np.sum((sub_mono_c == 1) & (c_vals == 1)))
        n00 = int(np.sum((sub_mono_c == 0) & (c_vals == 0)))

        paired_diff = acc - np.mean(sub_mono_c)

        # Exact two-sided binomial test on discordant pairs (McNemar exact)
        if n10 + n01 > 0:
            binom_res = stats.binomtest(n01, n10 + n01, p=0.5, alternative="two-sided")
            p_mcnemar_exact = binom_res.pvalue
        else:
            p_mcnemar_exact = 1.0

        # Paired bootstrap CI (10,000 resamples)
        rng = np.random.default_rng(42)
        diff_arr = c_vals - sub_mono_c
        boot_diffs = [np.mean(diff_arr[rng.integers(0, n, size=n)]) for _ in range(10000)]
        diff_ci_low = np.percentile(boot_diffs, 2.5)
        diff_ci_high = np.percentile(boot_diffs, 97.5)
        p_boot = 2.0 * min(np.mean(np.array(boot_diffs) <= 0), np.mean(np.array(boot_diffs) >= 0))
        p_boot = min(1.0, max(0.0, p_boot))

        # Token statistics
        mean_tok = np.mean(t_vals)
        median_tok = np.median(t_vals)
        total_tok = int(np.sum(t_vals))
        cost_ratio = mean_tok / np.mean(sub_mono_t) if np.mean(sub_mono_t) > 0 else 1.0

        # Operational rates
        interv_rate = np.mean(a_vals != "stop")
        false_interv = int(np.sum((a_vals != "stop") & (sub_mono_c == 1) & (c_vals == 0)))
        missed_benef = int(np.sum((a_vals == "stop") & (sub_mono_c == 0) & (sub_oracle_c == 1)))

        # Regret
        regret_arr = np.maximum(0.0, sub_oracle_c - c_vals) + 0.05 * np.maximum(0.0, t_vals - sub_oracle_t) / 6000.0
        norm_regret = np.mean(np.clip(regret_arr, 0.0, 1.0))

        rows.append({
            "subset": name,
            "sample_size": n,
            "method": m,
            "accuracy": acc,
            "acc_wilson_ci_low": ci_low,
            "acc_wilson_ci_high": ci_high,
            "paired_diff_vs_mono": paired_diff,
            "diff_boot_ci_low": diff_ci_low,
            "diff_boot_ci_high": diff_ci_high,
            "n_discordant_harmful_n10": n10,
            "n_discordant_beneficial_n01": n01,
            "mcnemar_exact_p": p_mcnemar_exact,
            "bootstrap_paired_p": p_boot,
            "mean_tokens": mean_tok,
            "median_tokens": median_tok,
            "total_tokens": total_tok,
            "cost_ratio": cost_ratio,
            "intervention_rate": interv_rate,
            "false_interventions": false_interv,
            "missed_beneficial": missed_benef,
            "normalized_regret": norm_regret
        })
    return rows

all_rows = []
# Overall
all_rows.extend(compute_metrics_for_subset(None, "Overall (N=100)"))
# DocVQA
doc_idx = inst_dset[inst_dset == "docvqa"].index
all_rows.extend(compute_metrics_for_subset(doc_idx, "DocVQA (N=50)"))
# ChartQA
chart_idx = inst_dset[inst_dset == "chartqa"].index
all_rows.extend(compute_metrics_for_subset(chart_idx, "ChartQA (N=50)"))

df_recomputed = pd.DataFrame(all_rows)
out_csv = Path("discovery/live_validation/recomputed_metrics.csv")
df_recomputed.to_csv(out_csv, index=False)
print(f"Saved recomputed metrics to {out_csv}")

print("\n=== RECOMPUTED METRICS OVERALL ===")
print(df_recomputed[df_recomputed["subset"] == "Overall (N=100)"][
    ["method", "accuracy", "paired_diff_vs_mono", "n_discordant_harmful_n10", "n_discordant_beneficial_n01", "mcnemar_exact_p", "bootstrap_paired_p", "cost_ratio", "normalized_regret"]
])

print("\n=== RECOMPUTED METRICS DOCVQA ===")
print(df_recomputed[df_recomputed["subset"] == "DocVQA (N=50)"][
    ["method", "accuracy", "paired_diff_vs_mono", "n_discordant_harmful_n10", "n_discordant_beneficial_n01", "mcnemar_exact_p", "cost_ratio", "normalized_regret"]
])

print("\n=== RECOMPUTED METRICS CHARTQA ===")
print(df_recomputed[df_recomputed["subset"] == "ChartQA (N=50)"][
    ["method", "accuracy", "paired_diff_vs_mono", "n_discordant_harmful_n10", "n_discordant_beneficial_n01", "mcnemar_exact_p", "cost_ratio", "normalized_regret"]
])
