# Pre-Registered Statistical Analysis Plan & Multiplicity Corrections

**Date:** October 11, 2026  
**Auditor:** Agent I (Statistical Reviewer)  
**Location:** `research_revision/STATISTICAL_ANALYSIS_PLAN.md`

---

## 1. Primary Statistical Hypotheses & Endpoints

### Primary Endpoint
Paired accuracy difference $\Delta_{\text{Acc}} = \text{Acc}(\pi_{\text{eval}}) - \text{Acc}(\pi_{\text{baseline}})$ evaluated on identical pre-registered document instances.

### Secondary Endpoints
1. Total token consumption per query $C(\pi)$.
2. Normalized empirical oracle regret $\mathcal{R}(\pi) \in [0, 1]$.
3. Truncation rate (fraction of completion responses hitting the $B_{\text{out}}$ token limit).

---

## 2. Statistical Testing & Estimation Methods

### A. Paired Binary Outcomes (McNemar's Exact Test)
Because all compared policies are evaluated on the exact same document instances, paired testing is mandatory. For two policies $\pi_1$ and $\pi_2$, we construct the $2 \times 2$ contingency table of discordant outcomes:
- $n_{10}$: Number of instances where $\pi_1$ is correct and $\pi_2$ is incorrect.
- $n_{01}$: Number of instances where $\pi_1$ is incorrect and $\pi_2$ is correct.

The exact two-sided binomial $p$-value is computed as:
$$p = 2 \cdot \sum_{k=0}^{\min(n_{10}, n_{01})} \binom{n_{10} + n_{01}}{k} \left(\frac{1}{2}\right)^{n_{10} + n_{01}}$$

### B. Multiple Testing Adjustment (Bonferroni)
For the family of primary baseline comparisons ($m = 3$ tests: GVoC vs. Monolithic, GVoC vs. Confidence Router, GVoC vs. MACT):
$$\alpha_{\text{adjusted}} = \frac{0.05}{3} \approx 0.0167$$
Statistical significance is reported only if the adjusted $p < 0.0167$.

### C. Interval Estimation
- **Task Accuracy:** 95% Wilson Score intervals:
  $$\hat{p} \pm \frac{z_{1-\alpha/2}}{1 + \frac{z_{1-\alpha/2}^2}{n}} \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z_{1-\alpha/2}^2}{4n^2}}$$
- **Token Counts & Regret:** Non-parametric percentile bootstrap with $B = 10,000$ resamples.

---

## 3. Power Analysis & Minimum Detectable Effect (MDE) Bounds

| Evaluation Partition | Sample Size ($N$) | Standard Error (SE) | 80% Power MDE ($\alpha=0.05$) | Interpretive Scope & Valid Inferences |
| :--- | :--- | :--- | :--- | :--- |
| **Offline Diagnostic Simulation** | 16,000 | $\approx \pm 0.35\%$ | **1.2%** | High statistical power. Small effects ($\ge 1.5\%$) are reliably detectable. |
| **Live Pilot Benchmark** | 100 | $\approx \pm 4.2\%$ | **14.5%** | Moderate power. Detects large effects ($\ge 15\%$), but underpowered for subtle differences ($\le 6\%$). Cannot prove equivalence. |
| **Exploratory Factorial Probe** | 20 | $\approx \pm 9.5\%$ | **35.0%** | Severely underpowered. Strictly exploratory; cannot confirm subtle distinctions. |

---

## 4. Multiplicity-Adjusted Audit of Empirical Findings

| Experimental Contrast | Sample Size ($N$) | Observed Performance | Raw $p$-value | Bonferroni Adjusted $p$ ($m=3$) | Statistical Conclusion |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **16k Simulation:** GVoC vs. MACT | 16,000 | 70.2% vs. 64.4% (+5.8%) | $p < 10^{-12}$ | $p < 10^{-11}$ | **Statistically Significant.** GVoC outperforms MACT under simulated grounded actions. |
| **16k Simulation:** GVoC vs. Conf Router | 16,000 | 70.2% vs. 61.1% (+9.1%) | $p < 10^{-15}$ | $p < 10^{-14}$ | **Statistically Significant.** GVoC outperforms confidence-based routing. |
| **Live Pilot ($N=100$):** Monolithic vs. GVoC | 100 | 82.0% vs. 72.0% (-10.0%) | $p = 0.0129$ | $p = 0.0387$ | **Statistically Significant Degradation.** Unregularized GVoC degrades accuracy on live models. |
| **Live Pilot ($N=100$):** Monolithic vs. C-GVoC | 100 | 82.0% vs. 76.0% (-6.0%) | $p = 0.1460$ | $p = 0.4380$ | **Not Statistically Significant.** Difference is inconclusive; does *not* prove preservation. |
| **Factorial Probe ($N=20$):** Crop (C4) vs. Low-Res (C2) | 20 | 25.0% vs. 60.0% (-35.0%) | $p = 0.0391$ | N/A (single exploratory probe) | **Significant Degradation.** Unguided cropping destroys peripheral context. |
