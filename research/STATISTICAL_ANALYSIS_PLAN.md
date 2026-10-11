# Statistical Analysis Plan & Multiplicity Corrections

**Document:** `research/STATISTICAL_ANALYSIS_PLAN.md`  
**Date:** October 10, 2026  
**Auditor:** Statistical Reviewer

---

## 1. Primary Hypothesis and Endpoints

### Primary Hypothesis
Allocating test-time compute to observation space via Grounded Value-of-Compute yields a statistically significant increase in task accuracy over procedural reasoning (MACT) while reducing total token consumption.

### Primary Metrics
1. **Paired Accuracy Difference ($\Delta_{\text{Acc}}$):** $\text{Acc}(\pi_1) - \text{Acc}(\pi_2)$ evaluated on identical query instances.
2. **Mean Token Reduction Ratio:** $(C(\pi_{\text{baseline}}) - C(\pi_{\text{GVoC}})) / C(\pi_{\text{baseline}})$.
3. **Empirical Regret Difference ($\Delta_{\mathcal{R}}$):** $\mathcal{R}(\pi_{\text{baseline}}) - \mathcal{R}(\pi_{\text{GVoC}})$.

---

## 2. Statistical Testing Framework

### A. Paired Binary Outcomes (McNemar's Exact Test)
Because all methods are evaluated on the exact same document instances, paired testing is mandatory.
For comparing two policies $\pi_1$ and $\pi_2$, we construct the $2 \times 2$ contingency table:
- $n_{11}$: Both $\pi_1$ and $\pi_2$ correct.
- $n_{10}$: $\pi_1$ correct, $\pi_2$ incorrect.
- $n_{01}$: $\pi_1$ incorrect, $\pi_2$ correct.
- $n_{00}$: Both incorrect.

The exact two-sided binomial $p$-value is computed as:
$$p = 2 \cdot \sum_{k=0}^{\min(n_{10}, n_{01})} \binom{n_{10} + n_{01}}{k} \left(\frac{1}{2}\right)^{n_{10} + n_{01}}$$

### B. Multiple Comparison Corrections (Bonferroni Adjustment)
For the family of primary benchmark contrasts ($m = 3$ tests: GVoC vs. Monolithic, GVoC vs. Confidence Router, GVoC vs. MACT):
$$\alpha_{\text{adjusted}} = \frac{0.05}{3} \approx 0.0167$$
Differences are declared statistically significant only if $p < 0.0167$.

### C. Interval Estimation
- **Binomial Proportions (Accuracy):** 95% Wilson Score intervals:
  $$\hat{p} \pm \frac{z_{1-\alpha/2}}{1 + \frac{z_{1-\alpha/2}^2}{n}} \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z_{1-\alpha/2}^2}{4n^2}}$$
- **Continuous Metrics (Tokens & Regret):** Non-parametric percentile bootstrap with $B = 10,000$ resamples.

---

## 3. Power Analysis & Minimum Detectable Effect (MDE)

| Sample Size ($N$) | Evaluation Partition | Standard Error (SE) | 80% Power MDE ($\alpha=0.05$) | Interpretive Scope |
| :--- | :--- | :--- | :--- | :--- |
| **16,000** | Diagnostic Benchmark Simulation | $\approx \pm 0.35\%$ | **1.2%** | High statistical power. Small effects ($\ge 1.5\%$) are reliably detectable. |
| **100** | Live Pilot Benchmark | $\approx \pm 4.2\%$ | **14.5%** | Moderate power. Detects large effects ($\ge 15\%$), but underpowered for subtle differences ($\le 6\%$). |
| **20** | Exploratory Factorial Probe | $\approx \pm 9.5\%$ | **35.0%** | Severely underpowered. Strictly exploratory; cannot confirm subtle distinctions. |

---

## 4. Multiplicity-Adjusted Audit of Empirical Findings

| Contrast | Sample Size ($N$) | Raw Observed Metric | Raw $p$-value | Bonferroni Adjusted $p$ ($m=3$) | Statistical Conclusion |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **16k Simulation:** GVoC vs. MACT | 16,000 | 70.2% vs. 64.4% (+5.8%) | $p < 10^{-12}$ | $p < 10^{-11}$ | **Statistically Significant.** GVoC outperforms MACT under simulated grounded actions. |
| **16k Simulation:** GVoC vs. Conf Router | 16,000 | 70.2% vs. 61.1% (+9.1%) | $p < 10^{-15}$ | $p < 10^{-14}$ | **Statistically Significant.** GVoC outperforms confidence-based routing. |
| **Live Pilot ($N=100$):** Monolithic vs. GVoC | 100 | 82.0% vs. 72.0% (-10.0%) | $p = 0.0129$ | $p = 0.0387$ | **Statistically Significant Degradation.** Unregularized GVoC degrades accuracy. |
| **Live Pilot ($N=100$):** Monolithic vs. C-GVoC | 100 | 82.0% vs. 76.0% (-6.0%) | $p = 0.1460$ | $p = 0.4380$ | **Not Statistically Significant.** Difference is inconclusive; does *not* prove preservation. |
| **Factorial Probe ($N=20$):** Crop (C4) vs. Low-Res (C2) | 20 | 25.0% vs. 60.0% (-35.0%) | $p = 0.0391$ | N/A (single exploratory probe) | **Significant Degradation.** Unguided cropping destroys peripheral context. |
