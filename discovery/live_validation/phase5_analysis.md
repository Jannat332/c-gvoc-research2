# Phase 5: Independent Empirical Analysis of Live VDU Pilot

**Date:** 2026-10-10 21:54:56
**Database Source:** `discovery/live_validation/live_evaluation.db`
**Evaluated Instances:** 100 (Genuine Multimodal Document & Chart Instances)
**Total Genuine API Calls:** 300 (100% Verified Live Inference, Zero Mocks)

## 1. Method Performance Comparison Table

| Method | Accuracy (95% CI) | Paired Diff vs Mono (95% CI) | p-value | Mean Tokens | Cost Ratio | Interv Rate | False Interv | Missed Benef | Norm Regret |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MONOLITHIC** | 82.0% [74.0, 89.0] | 0.0% (Ref) | - | 1428 | 1.00x | 0.0% | 0 | 3 | 0.0300 |
| **DETERMINISTIC** | 79.0% [71.0, 87.0] | -3.0% [-7.0, +0.0] | 0.0954 | 1566 | 1.10x | 15.0% | 3 | 2 | 0.0608 |
| **GVOC** | 72.0% [63.0, 81.0] | -10.0% [-17.0, -3.0] | 0.0046 | 2889 | 2.02x | 100.0% | 12 | 0 | 0.1409 |
| **CGVOC** | 76.0% [68.0, 84.0] | -6.0% [-13.0, +0.0] | 0.0956 | 1676 | 1.17x | 48.0% | 9 | 0 | 0.0914 |
| **ORACLE** | 85.0% [78.0, 91.0] | +3.0% [+0.0, +7.0] | 0.0882 | 1446 | 1.01x | 3.0% | 0 | 0 | 0.0000 |

*Note: Oracle is an offline counterfactual upper bound diagnostic, NOT a deployable online policy.*

## 2. Phase 4: Empirical Uncertainty Proxy Audit

- **Evaluated Action Branches:** 200 paired counterfactual evaluations across 100 unique documents.
- **Pearson Correlation r(sigma_a, eps_a):** `-0.2173` (p = `0.0020`, Clustered 95% CI: `[-0.3194, -0.1209]`).
- **Spearman Rank Correlation rho(sigma_a, eps_a):** `-0.1861` (p = `0.0083`).
- **Binned Error across Uncertainty Tertiles:**
  - Low sigma (< 0.49): Mean Absolute Error = `0.7084`
  - Mid sigma ([0.49, 0.68]): Mean Absolute Error = `0.5182`
  - High sigma (> 0.68): Mean Absolute Error = `0.5100`

> [!WARNING]
> **Uncertainty Proxy Invalidation:** The empirical correlation between the telemetry dispersion proxy and true counterfactual estimation error is near-zero or negative on live document data. Therefore, the proxy **CANNOT be claimed as calibrated epistemic uncertainty** or statistical standard error. It must be described strictly as a heuristic telemetry penalty.

## 3. Dataset-wise Breakdown (DocVQA vs ChartQA)

| Dataset | Sample Size | Monolithic Acc | C-GVoC Acc | Paired Diff | Oracle Bound |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DOCVQA** | 50 | 100.0% | 100.0% | +0.0% | 100.0% |
| **CHARTQA** | 50 | 64.0% | 52.0% | -12.0% | 70.0% |