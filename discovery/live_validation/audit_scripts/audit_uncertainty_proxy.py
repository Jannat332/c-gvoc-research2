import sqlite3
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

conn = sqlite3.connect("discovery/live_validation/live_evaluation.db")
df_diag = pd.read_sql_query("SELECT * FROM live_counterfactual_actions", conn)
conn.close()

print(f"Total rows in live_counterfactual_actions: {len(df_diag)}")
print(f"Unique instances: {df_diag['instance_id'].nunique()}")
print(f"Action breakdown:\n{df_diag['action'].value_counts()}")

# Variables
sigma = df_diag["sigma_proxy"].values
abs_err = df_diag["prediction_error"].values
signed_err = (df_diag["predicted_delta"] - df_diag["true_delta"]).values

# 1. Pearson and Spearman on Absolute Error
r_abs, p_r_abs = stats.pearsonr(sigma, abs_err)
rho_abs, p_rho_abs = stats.spearmanr(sigma, abs_err)

# 2. Pearson and Spearman on Signed Error
r_sign, p_r_sign = stats.pearsonr(sigma, signed_err)
rho_sign, p_rho_sign = stats.spearmanr(sigma, signed_err)

# Clustered Bootstrap for Pearson r (clustering by instance_id)
unique_insts = df_diag["instance_id"].unique()
n_insts = len(unique_insts)
rng = np.random.default_rng(42)

boot_r_abs = []
boot_rho_abs = []

for _ in range(10000):
    sample_insts = rng.choice(unique_insts, size=n_insts, replace=True)
    # Filter matching rows
    sample_df = df_diag[df_diag["instance_id"].isin(sample_insts)]
    if sample_df["sigma_proxy"].nunique() > 1 and sample_df["prediction_error"].nunique() > 1:
        b_r, _ = stats.pearsonr(sample_df["sigma_proxy"].values, sample_df["prediction_error"].values)
        b_rho, _ = stats.spearmanr(sample_df["sigma_proxy"].values, sample_df["prediction_error"].values)
        boot_r_abs.append(b_r)
        boot_rho_abs.append(b_rho)

ci_r_abs = (float(np.percentile(boot_r_abs, 2.5)), float(np.percentile(boot_r_abs, 97.5)))
ci_rho_abs = (float(np.percentile(boot_rho_abs, 2.5)), float(np.percentile(boot_rho_abs, 97.5)))

# Binned Analysis across Tertiles of sigma_proxy
tertiles = np.percentile(sigma, [33.33, 66.67])
bin_low = abs_err[sigma <= tertiles[0]]
bin_mid = abs_err[(sigma > tertiles[0]) & (sigma <= tertiles[1])]
bin_high = abs_err[sigma > tertiles[1]]

# Baseline comparison: Mean Absolute Error of Constant Predictor vs Linear Proxy
constant_prediction = np.mean(abs_err)
mae_constant = np.mean(np.abs(abs_err - constant_prediction))
mse_constant = np.mean((abs_err - constant_prediction)**2)

# Linear fit from sigma
slope, intercept, _, _, _ = stats.linregress(sigma, abs_err)
linear_pred = slope * sigma + intercept
mae_linear = np.mean(np.abs(abs_err - linear_pred))
mse_linear = np.mean((abs_err - linear_pred)**2)

print("\n=== ABSOLUTE ERROR CORRELATIONS ===")
print(f"Pearson r:  {r_abs:.4f} (p = {p_r_abs:.4f}), 95% Clustered CI: [{ci_r_abs[0]:.4f}, {ci_r_abs[1]:.4f}]")
print(f"Spearman rho: {rho_abs:.4f} (p = {p_rho_abs:.4f}), 95% Clustered CI: [{ci_rho_abs[0]:.4f}, {ci_rho_abs[1]:.4f}]")

print("\n=== SIGNED ERROR CORRELATIONS ===")
print(f"Pearson r:  {r_sign:.4f} (p = {p_r_sign:.4f})")
print(f"Spearman rho: {rho_sign:.4f} (p = {p_rho_sign:.4f})")

print("\n=== BINNED ERROR ANALYSIS (TERTILES) ===")
print(f"Tertile cutoffs: <= {tertiles[0]:.4f}, ({tertiles[0]:.4f}, {tertiles[1]:.4f}], > {tertiles[1]:.4f}")
print(f"Low Dispersion  (N = {len(bin_low)}): Mean Absolute Error = {np.mean(bin_low):.4f} +/- {np.std(bin_low)/np.sqrt(len(bin_low)):.4f}")
print(f"Mid Dispersion  (N = {len(bin_mid)}): Mean Absolute Error = {np.mean(bin_mid):.4f} +/- {np.std(bin_mid)/np.sqrt(len(bin_mid)):.4f}")
print(f"High Dispersion (N = {len(bin_high)}): Mean Absolute Error = {np.mean(bin_high):.4f} +/- {np.std(bin_high)/np.sqrt(len(bin_high)):.4f}")

print("\n=== PREDICTIVE ACCURACY VS CONSTANT BASELINE ===")
print(f"Constant Baseline: MAE = {mae_constant:.4f}, MSE = {mse_constant:.4f}")
print(f"Linear Fit Proxy:  MAE = {mae_linear:.4f}, MSE = {mse_linear:.4f}")
print(f"R-squared: {1 - (mse_linear / mse_constant):.4f}")

# Breakdown by Dataset
print("\n=== CORRELATIONS BY DATASET ===")
for dset in ["docvqa", "chartqa"]:
    sub = df_diag[df_diag["dataset"] == dset]
    r_sub, p_sub = stats.pearsonr(sub["sigma_proxy"], sub["prediction_error"])
    rho_sub, p_rho_sub = stats.spearmanr(sub["sigma_proxy"], sub["prediction_error"])
    print(f"{dset.upper()} (N={len(sub)} branches): Pearson r = {r_sub:.4f} (p={p_sub:.4f}), Spearman rho = {rho_sub:.4f} (p={p_rho_sub:.4f})")
