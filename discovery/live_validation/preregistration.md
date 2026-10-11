# Preregistered Experimental Protocol: Live Empirical Validation of GVoC and C-GVoC

**Auditors & Investigators:** Antigravity Research Engineering  
**Preregistration Date:** October 10, 2026  
**Repository:** `ESWA_ehte` / `naacl`  
**Target:** NAACL Empirical Validation Gate  
**Current Verdict:** Outcome B (Promising but Unvalidated) -> Live Empirical Gate  

---

## 1. Research Questions & Hypotheses

### Primary Research Question
Does Counterfactual Grounded Value-of-Compute (C-GVoC), which adjusts intervention advantage scores using an observation-space telemetry dispersion penalty, produce a measurable, statistically defensible improvement in task accuracy or compute efficiency compared to:
1. Monolithic / direct single-pass VLM inference,
2. Deterministic heuristic routing,
3. Original risk-neutral GVoC ($\lambda = 0$), and
4. A stop-only (no intervention) baseline,
on genuine visual document understanding tasks?

### Preregistered Hypotheses
- **$H_1$ (Accuracy Benefit):** C-GVoC achieves higher or equal accuracy compared to Monolithic inference on complex visual document questions.
- **$H_2$ (Uncertainty Proxy Correlation):** The empirical telemetry dispersion metric $\hat{\sigma}_a(s) = \sqrt{(1 - c_{\text{consensus}})^2 + d_{\text{layout}}^2 + d_{\text{evidence}}^2}$ exhibits a statistically positive correlation with the true absolute prediction error $\epsilon_a(s) = |y^* - \hat{y}_a|$ across held-out live intervention instances:
  $$\text{Pearson } r(\hat{\sigma}_a, \epsilon_a) > 0, \quad \text{Spearman } \rho(\hat{\sigma}_a, \epsilon_a) > 0.$$
- **$H_3$ (False Intervention Suppression):** Conservative penalization ($\lambda > 0$) strictly reduces false interventions (interventions that degrade or fail to improve an already correct monolithic response) compared to standard GVoC ($\lambda = 0$).
- **$H_0$ (Null Hypothesis):** C-GVoC confers no statistically detectable accuracy advantage over monolithic inference ($\Delta_{\text{acc}} \le 0$), and $\hat{\sigma}_a(s)$ is uncorrelated or negatively correlated with true prediction error ($r \le 0$).

---

## 2. Dataset Selection & Instance Freezing

To eliminate data leakage and post-hoc filtering:
- **Sample Size:** Exactly 100 genuine multimodal instances (50 DocVQA, 50 ChartQA).
- **DocVQA Set:** First 50 test instances from `nielsr/docvqa_1200_examples` (`docvqa_000` through `docvqa_049`).
  - Document domain: Industry scans, financial tables, invoices, tax filings, legal letters.
  - Multi-annotator ground truth answers preserved.
- **ChartQA Set:** First 50 test instances from `HuggingFaceM4/ChartQA` (`chartqa_000` through `chartqa_049`).
  - Chart domain: Bar charts, line graphs, scatter plots, multi-series diagrams.
  - Standard ground truth labels preserved.
- **No Exclusions:** All 100 instances are frozen into `discovery/live_validation/pilot_dataset/instances.json` prior to any model evaluation. No difficult or failing instance will be dropped post-hoc.

---

## 3. Compared Methods

All methods are evaluated on the exact same 100 frozen instances under identical prompt structures and image representations:

1. **Monolithic Direct Inference:**
   - Single-pass multimodal VLM call with full image and question.
   - Temperature: $0.0$, Max tokens: $150$.
   - Represents the zero-intervention test-time standard.
2. **Deterministic Routing Baseline:**
   - Checks confidence/consensus threshold; triggers a fixed high-resolution re-grounding intervention if confidence is below $0.70$.
3. **Original GVoC ($\lambda = 0$):**
   - Estimates expected accuracy delta $\hat{\Delta}_a(s)$ relative to stopping for each candidate action $a \in \{\text{STOP}, \text{REGROUND}, \text{REEXEC}, \text{VERIFY}, \text{ABSTAIN}\}$.
   - Action chosen via standard ratio routing: $a^* = \arg\max_a \frac{\hat{\Delta}_a(s)}{C(a)}$.
4. **C-GVoC ($\lambda = 0.5$):**
   - Applies the conservative telemetry dispersion penalty:
     $$\text{Score}(a) = \frac{\hat{\Delta}_a(s) - \lambda \hat{\sigma}_a(s)}{C(a)}.$$
   - Uses the preregistered penalty coefficient $\lambda = 0.5$.
5. **Stop-Only Baseline:**
   - Strictly terminates at the initial visual observation with zero additional calls.
6. **Observed-Action Counterfactual Oracle (Diagnostic Bound):**
   - **Explicit Disclaimer:** This is an offline counterfactual upper bound constructed from the best observed outcome among evaluated actions on each instance. It is NOT an executable deployment policy.

---

## 4. Evaluated Models

- **Primary Model:** Mistral Pixtral-12B (`pixtral-12b-2409`)
  - Direct Mistral AI endpoint with key pool rotation.
  - Verified multimodal visual OCR capabilities.
  - Deterministic greedy decoding (temperature = 0.0).
- **Secondary Cross-Model (Subset Validation):** Qwen2.5-VL-72B (`qwen/qwen2.5-vl-72b-instruct`) via OpenRouter API.

---

## 5. Scoring & Operational Definitions

- **Normalized Exact / Substring Match (ANLS / Relaxed Accuracy):**
  A response is scored as $1.0$ if the ground-truth string matches the parsed model output under case-insensitive whitespace-normalized substring or exact numeric equivalence; $0.0$ otherwise.
- **Intervention Frequency:**
  $$\text{Rate}_{\text{intervene}} = \frac{1}{N} \sum_{i=1}^N \mathbf{1}\{a_i \ne \text{STOP}\}.$$
- **False Intervention:**
  An intervention occurring on an instance where Monolithic was already correct, but the intervention either flipped the answer to incorrect or spent additional tokens without accuracy gain.
- **Normalized Regret:**
  $$\text{Regret} = \frac{1}{N} \sum_{i=1}^N \left( \text{Acc}_{\text{oracle}}(i) - \text{Acc}_{\text{method}}(i) + \alpha \frac{\max(0, \text{Tokens}_i - \text{Tokens}_{\text{oracle}, i})}{\text{MaxTokens}} \right).$$

---

## 6. Statistical Analysis Plan

- **Paired Bootstrap:** 10,000 bootstrap resamples across paired instance differences $\Delta = Y_{\text{C-GVoC}} - Y_{\text{Baseline}}$.
- **Confidence Intervals:** 95% two-sided percentile bootstrap confidence intervals.
- **Proxy Validation Analysis:**
  - Pearson correlation $r(\hat{\sigma}, \epsilon)$ and Spearman rank correlation $\rho(\hat{\sigma}, \epsilon)$.
  - Stratified binning of $\hat{\sigma}$ into low, medium, and high tertiles to measure monotonic error relationship.
- **Stopping & Failure Rule:**
  - Full evaluation runs until all 100 instances are processed.
  - If provider API returns persistent HTTP errors (>20% failure rate after retries), execution must halt and report the blocker per Rule 8. Mock fallback is strictly disabled.
