# Decisive Experiment Plan for Shortlisted Candidates

**Project:** *Think Longer or Look Closer? Test-Time Scaling for Visual Document Understanding*  
**Date:** 2026-10-10  
**Authors:** Experimental Specialist & Research Engineer

---

## 1. Experimental Objectives

We design the smallest decisive experiment to evaluate and compare the three shortlisted candidates against original GVoC and established baselines.

### The Decisive Questions:
1. **Candidate 1 (Risk-Bounded LCB):** Does penalizing epistemic uncertainty ($\kappa \cdot \hat{\sigma}_a$) improve the Accuracy--Compute--Regret Pareto frontier on held-out test data compared to point-estimate GVoC ($\kappa=0$)?
2. **Candidate 2 (Clean-State Gating):** Does deterministic clean-state suppression eliminate Type-I compute harm without suppressing beneficial repairs on corrupted documents?
3. **Candidate 3 (Harm-Aware Abstention):** Does explicitly estimating damage probability reduce intervention harm rate ($Y(\text{stop})=1 \to Y(a)=0$) compared to standard routing?

---

## 2. Experimental Design & Splits

### Benchmark Split Discipline:
- **Validation Fold ($N = 20$ Scenarios):**
  - Datasets: DocVQA (10 instances), ChartQA (10 instances).
  - Purpose: Hyperparameter tuning ($\kappa \in [0.0, 1.0]$, $\tau_{\text{clean}} \in [0.50, 0.85]$, $\tau_{\text{safe}} \in [0.30, 0.60]$).
- **Held-Out Test Fold ($N = 20$ Scenarios):**
  - Datasets: TableBench (10 instances), MMLongBench-Doc (10 instances).
  - Purpose: Unbiased evaluation of policy generalization on unseen document layouts.

### Evaluated Methods:
1. `monolithic`: Zero-recovery baseline (always stop).
2. `fixed_veccap`: Deterministic heuristic rules (prior submission baseline).
3. `confidence_router`: Routes purely by average semantic confidence.
4. `mact`: Multi-agent collaborative tuning baseline.
5. `gvoc_point_estimate`: Original GVoC ($\kappa = 0.0$, point-estimate advantage).
6. `gvoc_clean_gated`: GVoC + Clean-state suppression only ($\kappa = 0.0$).
7. `gvoc_risk_bounded`: Full C-GVoC (LCB uncertainty penalty + clean suppression + safe abstention).
8. `gvoc_harm_aware`: Decomposed repair/harm modeling.
9. `oracle`: Loss-minimizing upper bound from empirical branches.

### Evaluation Metrics:
- **Task Accuracy (%):** Percentage of queries answered correctly.
- **Tokens / Query:** Total prompt + completion tokens consumed.
- **Oracle Regret:** Evaluated under mathematically verified normalized loss $\text{Loss} = 0.85 \mathbb{I}[Y=0] + 0.15 \frac{C}{C_{\max}}$.
- **Intervention Harm Rate (%):** Rate at which an active intervention breaks an already-correct answer ($Y(\text{stop})=1 \to Y(a)=0$).
- **Decision Latency (ms):** Wall-clock execution time of the controller per decision step.
- **95% Bootstrap Confidence Intervals:** Computed over 1,000 paired resamples.

---

## 3. Directory Layout for Prototypes

Prototypes and test results will be stored under:
- `discovery/experiments/candidate_1_risk_bounded/`
- `discovery/experiments/candidate_2_clean_gated/`
- `discovery/experiments/candidate_3_harm_aware/`
- `discovery/experiments/head_to_head_comparison.py`
