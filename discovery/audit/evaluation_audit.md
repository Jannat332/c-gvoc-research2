# Experimental Evaluation & Protocol Audit

**Author:** Experimental Research Specialist  
**Project:** *Think Longer or Look Closer? Test-Time Scaling for Visual Document Understanding*  
**Date:** 2026-10-10  
**Audit Scope:** Benchmark data, splits, baselines, statistical significance, and reproducibility.

---

## 1. Benchmark Data and Split Provenance

### 1.1 The Two Evaluation Layers in the Codebase
The repository contains two distinct evaluation layers:
1. **Full 16,000-Episode Simulation Suite (`gvoc_engine/experiments/run_full_16k_benchmark.py`):**
   - 4 Datasets: DocVQA (1k), ChartQA (1k), TableBench (1k), MMLongBench-Doc (1k) stored in `gvoc_engine/data/*.jsonl`.
   - 4 Simulated Foundation Models: Gemini 3.6 Flash, Pixtral 12B, Llama 3.2 Vision 11B, Qwen 2.5-VL 7B.
   - Evaluates 6 baselines per episode ($16,000 \times 6 = 96,000$ evaluations).
   - Generates Table 1, Table 2 (Model breakdowns), and Table 6 (Master Matrix) in the manuscript.
   - **Nature of Execution:** Uses deterministic perturbation responses (`apply_visual_document_perturbation`) and effective intervention sets (`get_effective_intervention_set`) rather than live multi-hour cloud API calls for all 96,000 runs. Runs in $\approx 20$ seconds on CPU.
2. **Fresh Diagnostic Paired Benchmark (`gvoc_engine/benchmark/fresh_benchmark_loader.py`):**
   - 40 concrete, fully-specified multimodal scenarios (10 per dataset).
   - Used by `run_risk_bounded_evaluation.py` and `run_pilot.py` for fine-grained counterfactual branching and bootstrap confidence intervals.
   - 160 paired intervention branches executed from identical frozen states.

### 1.2 Data Leakage & Split Discipline
- In `run_risk_bounded_evaluation.py`, validation data (DocVQA, ChartQA; $N=20$) is used to tune risk parameter $\kappa^* = 0.10$.
- Held-out test evaluation is performed exclusively on unseen domains (TableBench, MMLongBench; $N=20$).
- No instance identifiers or image assets overlap between the tuning split and test evaluation.

---

## 2. Baseline Implementation Integrity

| Baseline | Implementation Class / Function | Protocol Integrity | Notes / Vulnerabilities |
|---|---|---|---|
| **Monolithic Zero-Shot** | `MonolithicBaseline` | HIGH | Correctly executes single-pass answer without recovery intervention. Token cost fixed at 250 tokens. |
| **Fixed VEC-CAP (Deterministic Rule)** | `FixedVECCAPBaseline` | HIGH | Prior heuristic rule ($D_{\text{layout}} \ge 0.20 \implies \text{REGROUND}$, etc.). Intervenes aggressively on $>85\%$ of queries. |
| **Confidence-Based Router** | `ConfidenceRouterBaseline` | HIGH | Thresholds semantic confidence $\bar{C} = (c_{\text{plan}} + c_{\text{exec}} + c_{\text{judg}})/3$. Re-executes on moderate confidence ($[0.40, 0.85]$). |
| **MACT (Yu et al., 2026)** | `MACTBaseline` | MODERATE | Models agent-level budget re-allocation. Does not zoom in on pixels; allocates extra tokens to weakest reasoning agent. |
| **Empirical Oracle ($\mathcal{A}^*$)** | `OracleGVoCRouter` | HIGH | Selects the action that empirically maximizes accuracy gain per cost from held-out branches. Regret = 0 by definition. |

---

## 3. Statistical Testing and Confidence Intervals

### 3.1 Reported Uncertainty Intervals ($\pm$)
- In Table 1:
  - Monolithic: $12.5 \pm 0.5\%$
  - Confidence Router: $61.1 \pm 0.8\%$
  - MACT: $64.4 \pm 0.7\%$
  - Deterministic Rule: $89.0 \pm 0.5\%$
  - GVoC: $70.2 \pm 0.7\%$
  - C-GVoC: $70.4 \pm 0.7\%$
- **Statistical Unit:** The reported $\pm$ corresponds to a 95% confidence interval derived from binomial standard error $\pm 1.96 \sqrt{\frac{p(1-p)}{N}}$ with $N = 16,000$.
  - For $p = 0.702, N = 16,000$: $\text{SE} = \sqrt{\frac{0.702 \times 0.298}{16000}} = 0.00361$ ($0.36\%$).
  - $1.96 \times 0.36\% = \pm 0.71\%$, matching the reported $\pm 0.7\%$.
- **Hypothesis Testing:**
  - Difference between GVoC (70.2%) and MACT (64.4%) is $+5.8\%$.
  - Two-proportion z-test yields $z = \frac{0.702 - 0.644}{\sqrt{\frac{0.702 \times 0.298}{16000} + \frac{0.644 \times 0.356}{16000}}} = 11.23$, giving $p < 10^{-15}$ ($p < 0.001$).
  - The claim of statistical significance over MACT is verified.

---

## 4. Key Strengths and Honest Limitations of the Evaluation

### Strengths:
1. **Counterfactual Paired Alignment:** The branching protocol evaluates all candidate interventions starting from the exact same frozen intermediate state $s_t$, ensuring true causal comparison without trajectory drift confounding.
2. **Deterministic Baseline Acknowledgment:** The manuscript honestly reports that the Deterministic Rule baseline achieves highest raw accuracy (89.0%), properly framing GVoC as a compute-constrained Pareto optimizer (70.2% acc with 274 tokens vs 368 tokens).
3. **Multi-Domain Diversity:** Covers invoices (DocVQA), charts (ChartQA), spreadsheets (TableBench), and multi-page documents (MMLongBench).

### Limitations / Critical Notes:
1. **Simulated Benchmark vs Live VLM Inferences:** The 16,000-query benchmark is a simulated execution using perturbation models and heuristic response models. While fast and reproducible, this distinction must be clearly stated in the paper to avoid misleading reviewers that 384,000 live API calls to proprietary frontier models were paid for.
2. **Oracle Regret Scaling:** As noted in `math_audit.md`, the hardcoded legacy multipliers (6.71, 2.65) must be replaced with the mathematically normalized $[0, 1]$ regret metric.
