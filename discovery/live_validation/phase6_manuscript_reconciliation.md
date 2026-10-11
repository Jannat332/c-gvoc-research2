# Phase 6: Manuscript Scientific Reconciliation Audit

**Auditor / Reviewer:** NAACL Methodology Auditor & Senior Research Engineer  
**Date:** October 10, 2026  
**Target Manuscript:** `naacl/main.tex`  
**Current Paper:** *Think Longer or Look Closer? Test-Time Scaling for Visual Document Understanding*  

---

## 1. Provenance Classification of Every Manuscript Claim

| Manuscript Location | Headline Claim | Historical Classification | Reconciled Audit Classification | Action Taken in Manuscript |
| :--- | :--- | :--- | :--- | :--- |
| **Abstract (p. 1)** | "70.2% accuracy across 16,000 queries (+5.8 points over debate, -23.7% tokens)" | Simulated as live inference | **Offline Simulation Benchmark** | Explicitly qualify as 16,000-query offline diagnostic simulation across 4 benchmark distributions. |
| **Abstract (p. 1)** | Live empirical pilot claims | Absent | **Live Model Evaluation** | Add live empirical pilot results (Mistral Pixtral-12B) showing C-GVoC eliminates over-intervention. |
| **Table 1 (p. 1)** | Table 1 performance numbers ($N = 16,000$) | Unlabeled / Ambiguous | **Offline Simulation Benchmark** | Relabel table and caption explicitly as modeled counterfactual perturbation simulation. |
| **Section 3.2 (p. 2)** | "Calibrated epistemic uncertainty $\hat{\sigma}_a(s)$" | Unvalidated Bayesian claim | **Heuristic Telemetry Penalty** | Remove "calibrated epistemic uncertainty"; rename to "empirical telemetry dispersion penalty". |
| **Section 3.2 (p. 2)** | "Elimination of Type-I errors" | Unbounded guarantee | **Empirical Risk Suppression** | Replace absolute guarantee with "empirically suppresses spurious intervention on clear documents". |
| **Section 3.3 (p. 3)** | Data Processing Inequality limit | Theoretical claim | **Analytical Result** | Narrow assumptions: valid strictly under markovian post-processing of degraded observations. |
| **Section 4.1 (p. 3)** | Generalization across 4 model families | Claimed as live multi-model | **Simulation Across Modeled Backbones** | Clarify that 16k multi-model matrix was offline simulation; live pilot evaluated on Mistral Pixtral-12B. |
| **Table 2 (New)** | Live Empirical Pilot Table ($N = 50$) | New live artifact | **Live Model Evaluation** | Insert live evaluation table with paired bootstrap CIs, actual provider tokens, and regret. |

---

## 2. Theoretical Claims Audit

### A. Data Processing Inequality (Section 2 / Appendix A)
- **Claim:** $I(Y; \hat{Y}_{\text{reasoning}} \mid X_{\text{low-res}}) \le I(Y; X_{\text{low-res}})$.
- **Audit:** The standard Data Processing Inequality (Cover & Thomas, 2006) states that if $Y \to X \to Z$ forms a Markov chain, then $I(Y; Z) \le I(Y; X)$. When an image is downsampled ($X_{\text{high-res}} \to X_{\text{low-res}}$), the mutual information $I(Y; X_{\text{low-res}})$ is upper bounded by $I(Y; X_{\text{high-res}})$. Any subsequent reasoning tokens $Z$ generated purely from $X_{\text{low-res}}$ satisfy $Y \to X_{\text{low-res}} \to Z$, meaning $I(Y; Z) \le I(Y; X_{\text{low-res}})$.
- **Status:** **Mathematically Sound**, provided the Markov chain assumption holds (i.e., the reasoning process has no side-channel access to the high-resolution sensor pixels).

### B. Ratio-Routing Optimality (Proposition 1)
- **Claim:** Greedy selection by $\frac{\Delta P_a}{C_a}$ optimizes incremental accuracy under linear budget constraints.
- **Audit:** This is the classical fractional knapsack relaxation (Dantzig, 1957; Russell & Wefald, 1991). In discrete sequential decision making, greedy ratio routing is an approximation with a factor $(1 - 1/e)$ under submodularity, but not strictly optimal for arbitrary non-linear budgets.
- **Status:** **Valid as a Greedy Heuristic Approximation**, but must be labeled as an approximation rather than an exact global optimum.

---

## 3. Mandatory Reductions & Qualifying Language

1. **Remove "16,000 Live Inferences":** No reader or reviewer must infer that 16,000 live API calls were performed across Google, Mistral, Groq, and Qwen. The 16,000-query benchmark is explicitly documented as a high-throughput offline diagnostic simulation.
2. **Qualify the Uncertainty Formulation:** The metric $\hat{\sigma}_a(s)$ is an empirical proxy reflecting layout and evidence divergence. We honestly report that while its rank correlation is statistically significant ($\rho = 0.354, p < 0.01$), its linear correlation is weak ($r \approx 0.10$).
3. **Report the True Effect of C-GVoC:** C-GVoC's value is in **risk containment**: preventing unregularized GVoC from destroying accuracy and burning double the token budget on clean documents.
