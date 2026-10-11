# Reanalysis of Uncertainty Proxy and Counterfactual Error

**Auditor:** Empirical Research & Methodology Auditor  
**Date:** October 10, 2026  
**Artifact Scope:** Raw diagnostic table `live_counterfactual_actions` in `discovery/live_validation/live_evaluation.db`  
**Evaluation Object:** The empirical dispersion proxy $\hat{\sigma}_a(s)$ used in C-GVoC's decision rule $U_{\text{conservative}}(a) = \hat{\Delta}_a(s) - \lambda \hat{\sigma}_a(s)$.

---

## 1. Provenance and Scope of Evaluation Records

The diagnostic records were evaluated directly from the raw database table `live_counterfactual_actions`:
- **Total Diagnostic Rows:** $N = 200$ evaluated counterfactual action branches.
- **Unique Instances:** $N_{\text{instances}} = 100$ frozen benchmark documents (50 DocVQA, 50 ChartQA).
- **Action Breakdown:** Exactly 100 rows for `action = 'reground'` and 100 rows for `action = 'reexecute'`.
- **True Counterfactual Outcomes:** Obtained from **actual live inference API calls** to Mistral Pixtral-12B (`pixtral-12b-2409`) recorded under `call_role = 'reground'` and `call_role = 'reexec'`. There are **zero synthetic, mock, or imputed labels** in this table.
- **Independent Evaluation:** The proxy $\hat{\sigma}_a(s)$ and advantage predictions $\hat{\Delta}_a(s)$ were evaluated purely out-of-sample on the 100 test instances without parameter retuning.

---

## 2. Statistical Correlation with Prediction Error

The central hypothesis of C-GVoC is that $\hat{\sigma}_a(s)$ quantifies epistemic uncertainty, meaning higher $\hat{\sigma}$ should indicate higher expected error $|\hat{\Delta}_a(s) - \Delta_{\text{true}}(a)|$ in the advantage estimator.

### A. Absolute Prediction Error ($|\hat{\Delta} - \Delta_{\text{true}}|$)
Because two action branches are evaluated per document, the 200 observations are clustered within 100 document instances. To account for intra-cluster correlation, 95% confidence intervals were computed using **10,000 cluster-bootstrap resamples** (resampling unique document instances with replacement):

- **Pearson Correlation ($r$):**
  $$\mathbf{r = -0.2173} \quad (p = 0.0020), \quad 95\% \text{ Clustered CI: } [-0.3173, -0.1186]$$
- **Spearman Rank Correlation ($\rho$):**
  $$\mathbf{\rho = -0.1861} \quad (p = 0.0083), \quad 95\% \text{ Clustered CI: } [-0.3075, -0.0706]$$

**Result:** The correlation between the dispersion proxy and absolute prediction error is **statistically significantly negative**. Higher proxy values are associated with *lower* prediction error, directly violating the required property of an uncertainty estimator.

### B. Signed Prediction Error ($\hat{\Delta} - \Delta_{\text{true}}$)
- **Pearson Correlation ($r$):**
  $$r = -0.1390 \quad (p = 0.0496)$$
- **Spearman Rank Correlation ($\rho$):**
  $$\rho = -0.1048 \quad (p = 0.1397, \text{not significant})$$

---

## 3. Binned Error Analysis Across Dispersion Tertiles

To examine non-linear calibration, the 200 records were partitioned into tertiles based on $\hat{\sigma}_a(s)$:

| Dispersion Tertile | Proxy Range ($\hat{\sigma}$) | Count ($N$) | Mean Absolute Error | Standard Error |
| :--- | :--- | :--- | :--- | :--- |
| **Low Dispersion** | $\le 0.4931$ | 76 | **0.7084** | $\pm 0.0521$ |
| **Mid Dispersion** | $(0.4931, 0.6842]$ | 114 | **0.5182** | $\pm 0.0315$ |
| **High Dispersion** | $> 0.6842$ | 10 | **0.5100** | $\pm 0.0939$ |

### Critical Finding on Binning:
Instances where the controller reported **lowest dispersion** exhibited the **highest prediction error** ($0.7084$), while instances flagged with highest dispersion exhibited substantially lower error ($0.5100$). The monotonic risk-ordering assumed by Lower Confidence Bound (LCB) methods is inverted in practice.

---

## 4. Explanatory Power vs. Baseline Predictors

We compare a linear model predicting absolute error from $\hat{\sigma}_a(s)$ against a naive constant predictor (predicting the sample mean error $\bar{e} = 0.5898$):

- **Constant Baseline Predictor:**
  - Mean Absolute Error (MAE): **0.3152**
  - Mean Squared Error (MSE): **0.1557**
- **Linear Fit from Proxy ($\hat{\sigma}$):**
  - Mean Absolute Error (MAE): **0.3060**
  - Mean Squared Error (MSE): **0.1483**
- **Coefficient of Determination ($R^2$):**
  $$\mathbf{R^2 = 0.0472}$$

**Result:** The proxy accounts for only **4.7% of the variance** in prediction error. Ninety-five percent of error variance is unmodeled by the dispersion proxy.

---

## 5. Dataset-Stratified Correlation Dissection

When stratified by benchmark distribution, the correlation patterns reveal extreme heterogeneity:

- **DocVQA ($N = 100$ branches):**
  - Pearson $r = +0.0589 \quad (p = 0.5606, \text{no linear correlation})$
  - Spearman $\rho = +0.2880 \quad (p = 0.0037, \text{weak positive rank correlation})$
- **ChartQA ($N = 100$ branches):**
  - Pearson $r = -0.1491 \quad (p = 0.1386, \text{not significant})$
  - Spearman $\rho = +0.1598 \quad (p = 0.1122, \text{not significant})$

In neither individual dataset is Pearson correlation statistically significant. The overall negative correlation ($r = -0.2173$) emerges largely from Simpson's paradox across dataset clusters: DocVQA had lower average $\hat{\sigma}$ but high monolithic accuracy (leading to large negative $\Delta$ when unhelpful interventions were tested), whereas ChartQA had higher average $\hat{\sigma}$.

---

## 6. Audit Verdict and Scope of Conclusions

1. **Specific Empirical Verdict:**
   The heuristic dispersion proxy $\hat{\sigma}_a(s)$ evaluated in this live experiment **does not function as a valid epistemic uncertainty estimator for decision error**. It exhibits a negative correlation with true error and explains less than 5% of error variance.
2. **Correct Scientific Terminology:**
   The parameter $\hat{\sigma}_a(s)$ must be labeled strictly as an **uncalibrated empirical dispersion heuristic**, not "Bayesian epistemic uncertainty" or "calibrated risk."
3. **Appropriate Generalization Boundary:**
   This finding does **not** prove that all uncertainty estimation for vision-language models is impossible. It proves specifically that:
   - Combining logprob variance and Sobel edge energy into an uncalibrated scalar proxy does not predict test-time intervention error.
   - Using this proxy in an LCB penalty ($\hat{\Delta} - \lambda \hat{\sigma}$) does not provide theoretical risk bounds.
