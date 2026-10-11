# Adjudication & Specification of the Winning Method

**Author:** Independent Scientific Adjudicator  
**Consortium:** Literature Specialist, Mathematical Specialist, Experimental Specialist, Skeptical Reviewer, Research Engineer  
**Date:** 2026-10-10  
**Selected Method:** Conservative Grounded Value-of-Compute (C-GVoC) with Telemetry-Conditioned LCB Penalization and Clean-State Suppression Gating.

---

## 1. Adjudication Analysis of the Three Prototypes

| Evaluation Criterion | Candidate 1: Risk-Bounded LCB | Candidate 2: Clean Gating Only | Candidate 3: Harm-Aware Decomposed |
|---|---|---|---|
| **Novelty vs Prior Work** | **HIGH**: Integrates telemetry-conditioned dispersion into VLM test-time routing. | **MODERATE**: Heuristic two-stage threshold filter. | **MODERATE**: Decomposed probabilities require extra assumptions. |
| **Mathematical Soundness** | **HIGH**: Formal LCB formulation $\max(0, \hat{\Delta P} - \kappa \hat{\sigma}) / (C + \epsilon)$. | **MODERATE**: Discontinuous rule. | **MODERATE**: Estimating $P(\text{Harm})$ is noisy due to rare harm events (<2%). |
| **Empirical Token Savings** | $-12.1$ tokens/query overall; $-23.4$ tokens on active subset. | $-12.1$ tokens/query. | **$-24.5$ tokens/query** (closest to Oracle). |
| **Type-I Error Elimination** | **0.0%** (Suppresses spurious clean repairs). | **0.0%**. | **0.0%**. |
| **Held-Out Generalization** | **CONFIRMED**: Drops test regret from 0.0096 to 0.0061. | **CONFIRMED**: Drops test regret to 0.0061. | Drops test regret to 0.0023, but risk of over-suppressing borderline repairs. |
| **System Complexity** | Plug-and-play LCB penalty (<0.02 ms CPU latency). | Extremely simple. | Adds $P(\text{Harm})$ and $\lambda_{\text{harm}}$ hyperparameters. |

### Adjudication Decision:
The winning method is **Conservative Grounded Value-of-Compute (C-GVoC)**, which integrates:
1. **Telemetry-Conditioned LCB Penalization:** Subtracting $\kappa \cdot \hat{\sigma}_a(s)$ from estimated advantage to prevent over-committing to unverified actions on boundary states.
2. **Clean-State Suppression:** Bypassing active tools when initial geometry is clean ($d_{\text{layout}} < 0.15$) and baseline answer confidence is high ($P_{\text{stop}} \ge 0.70$).
3. **Hierarchical Safe Abstention:** Explicitly distinguishing uncertainty about action benefit (where the model falls back to $a_{\text{stop}}$) from truly insufficient evidence (where $P_{\text{stop}} < \tau_{\text{safe}}$ and active repair is unviable, triggering $a_{\text{abstain}}$).

---

## 2. Formal Mathematical Specification

### 2.1 The Decision Problem
At test time, the system observes a query $\mathcal{Q}$ and an initial downsampled document image $\mathcal{I}_{\text{down}}$. It decodes an initial answer candidate $\hat{Y}_0$ and extracts a 16-D diagnostic state telemetry vector $f(s_t) \in \mathbb{R}^{16}$.

The controller must choose an action $a \in \mathcal{A} = \{a_{\text{stop}}, a_{\text{reground}}, a_{\text{reexec}}, a_{\text{abstain}}\}$ to maximize answer accuracy subject to token cost budget $B_t$.

### 2.2 Telemetry-Conditioned Dispersion Estimator
The epistemic standard error proxy $\hat{\sigma}_a(s)$ is parameterized as:
$$\hat{\sigma}_a(s) = \sqrt{\sigma_{0,a}^2 + w_c (1 - c_{\text{consensus}})^2 + w_l (d_{\text{layout}}^2 + d_{\text{evidence}}^2)}$$
bounded in $[0.03, 0.40]$, capturing the dispersion of advantage estimates under multimodal ambiguity.

### 2.3 Conservative Lower Confidence Bound (LCB) Score
$$\mathcal{V}_{\text{LCB}}(s, a) = \frac{\max\big(0,\; \hat{\Delta P}_a(s) - \kappa \cdot \hat{\sigma}_a(s)\big)}{C(s, a) + \epsilon}$$
where:
- $\hat{\Delta P}_a(s) = P(Y=1 \mid s, a) - P(Y=1 \mid s, a_{\text{stop}})$ is the estimated counterfactual accuracy improvement over stopping.
- $\kappa \ge 0$ is the conservatism parameter tuned on validation data ($\kappa^* = 0.10$ on pilot validation, $\kappa = 0.40$ on full benchmark).
- $C(s, a) > 0$ is the expected token cost of the intervention.
- $\epsilon = 10^{-4}$ prevents division by zero.

### 2.4 Decision Policy Hierarchy
$$\pi(s) = \begin{cases}
a_{\text{stop}}, & \text{if } d_{\text{layout}} < 0.15 \land d_{\text{evidence}} < 0.15 \land P(Y=1 \mid s, a_{\text{stop}}) \ge 0.70 \\
\arg\max_{a \in \mathcal{M}(s)} \mathcal{V}_{\text{LCB}}(s, a), & \text{if } \max_{a \in \mathcal{M}(s)} \mathcal{V}_{\text{LCB}}(s, a) > \tau \\
a_{\text{abstain}}, & \text{if } \max_{a} \mathcal{V}_{\text{LCB}}(s, a) \le \tau \land P(Y=1 \mid s, a_{\text{stop}}) < \tau_{\text{safe}} \\
a_{\text{stop}}, & \text{otherwise (conservative stopping)}
\end{cases}$$
where $\mathcal{M}(s) = \{a \in \mathcal{A}_{\text{active}} \mid \text{Cost}(a) \le B_t \land P(Y=1 \mid s, a) \ge 0.45\}$ enforces feasibility.

---

## 3. Preserved Negative Results & Scientific Integrity

1. **Deterministic Baseline Superiority in Raw Accuracy:** The Deterministic Rule baseline (`fixed_veccap`) achieves 89.0%--90.0% raw accuracy by unconditionally firing interventions on $>85\%$ of queries. C-GVoC does not beat the Deterministic Rule in raw accuracy; instead, it matches its 90.0% accuracy while saving tokens and achieving lowest oracle regret.
2. **MACT Outperforms on Reasoning Arithmetic:** On ChartQA arithmetic queries, multi-agent debate (MACT) outperforms GVoC (78.7% vs 56.6%) because optical zooming does not provide scratchpad arithmetic calculation.
3. **Simulated Benchmark Disclosure:** The 16,000-query benchmark is an offline perturbation simulation, not 384,000 live API calls to proprietary cloud models.
