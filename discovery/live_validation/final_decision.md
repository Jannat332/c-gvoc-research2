# Phase 7: Final Decision Gate — Scientific Audit & Empirical Verdict

**Reviewer / Research Engineer:** Antigravity Research Engineering & Skeptical NAACL Reviewer  
**Date:** October 10, 2026  
**Final Audit Verdict:** **Outcome C — The Central Empirical Claim of Unregularized GVoC is Contradicted on Real Documents; Outcome B for C-GVoC as a Partial Risk Guardrail.**  
**Consolidated Status Verdict:** **Outcome B: Promising but Deficient / Unvalidated for NAACL Submission.**  

---

## 1. Formal Verdict and Core Finding

### Final Gate Verdict: **OUTCOME B**
The empirical evidence collected from 300 genuine multimodal model calls across 100 frozen benchmark instances confirms that:

1. **The Central Empirical Claim of Original GVoC is Contradicted on Real Multimodal Tasks:**  
   In the offline 16k simulation, GVoC claimed a massive +57-point improvement over monolithic inference (70.2% vs 12.5%). In live empirical reality on genuine document and chart tasks (Mistral Pixtral-12B), monolithic zero-shot direct inference achieves **82.0%** accuracy.  
   Unregularized GVoC ($\lambda = 0.0$) triggers interventions on 100% of queries, causing severe **Type-I intervention inflation**: token consumption doubles (2,889 vs 1,428 tokens, **+102.3% compute explosion**) and accuracy **drops by -10.0 points** (from 82.0% down to 72.0%, paired bootstrap $p = 0.0046$, statistically significant degradation with 12 false interventions).
2. **C-GVoC Mitigates Over-Intervention but Remains an Incomplete Guardrail:**  
   C-GVoC ($\lambda = 0.5$) uses the observation-space dispersion penalty to suppress spurious interventions (cutting intervention rate from 100% to 48%, and false interventions from 12 to 9). It reduces token consumption by 42% compared to GVoC (1,676 vs 2,889 tokens) and lifts accuracy over GVoC (76.0% vs 72.0%). However, it **still underperforms monolithic direct inference by -6.0 points** (76.0% vs 82.0%).
3. **The Uncertainty Proxy is Definitively Invalidated as Epistemic Uncertainty:**  
   Across 200 held-out counterfactual branch evaluations, the telemetry dispersion metric $\hat{\sigma}_a(s)$ exhibits a **statistically significant negative correlation** with true advantage prediction error:
   $$\text{Pearson } r = -0.2173 \quad (p = 0.0020), \quad \text{Spearman } \rho = -0.1861 \quad (p = 0.0083).$$
   The metric does NOT measure estimation error; in fact, error is highest when dispersion is low (0.7084) and lowest when dispersion is high (0.5100). Describing $\hat{\sigma}_a(s)$ as "calibrated epistemic uncertainty" or a "statistical standard error" in an academic manuscript is scientifically false.

---

## 2. Experimental Ledger & Provenance Verification

- **Total Genuine Live API Calls:** Exactly 300 calls (100% external API calls to Mistral AI endpoint, 0% mocks, 0% cached).
- **Unique Frozen Benchmark Instances:** Exactly 100 instances (50 DocVQA from `nielsr/docvqa_1200_examples`, 50 ChartQA from `HuggingFaceM4/ChartQA`).
- **Tested Model:** Mistral Pixtral-12B (`pixtral-12b-2409`) at temperature 0.0.
- **Provider API Reliability:** 0 failed calls, 0 unhandled timeouts, 100% successful response parsing.
- **Mock Fallback Status:** Strictly disabled in `discovery/live_validation/live_runner.py`.
- **Reproducibility Database:** Fully archived in `discovery/live_validation/live_evaluation.db`.

---

## 3. Recomputed Empirical Comparison Table

*(Recomputed independently from raw database records via `discovery/live_validation/independent_analysis.py` across all $N = 100$ instances)*

| Method | Evaluation Type | Accuracy (95% CI) | Paired Diff vs Mono (95% CI) | p-value | Mean Tokens | Cost Ratio | False Interv | Norm Regret |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Monolithic Direct** | Live Model (Pixtral-12B) | **82.0%** [74.0, 89.0] | 0.0% (Reference) | - | **1,428** | **1.00x** | **0** | **0.0300** |
| **Deterministic Baseline** | Live Model (Pixtral-12B) | **79.0%** [71.0, 87.0] | -3.0% [-7.0, +0.0] | 0.0954 | 1,566 | 1.10x | 3 | 0.0608 |
| **Original GVoC ($\lambda = 0$)** | Live Model (Pixtral-12B) | **72.0%** [63.0, 81.0] | **-10.0%** [-17.0, -3.0] | **0.0046** | **2,889** | **2.02x** | **12** | **0.1409** |
| **C-GVoC ($\lambda = 0.5$, Ours)** | Live Model (Pixtral-12B) | **76.0%** [68.0, 84.0] | **-6.0%** [-13.0, +0.0] | 0.0956 | **1,676** | **1.17x** | **9** | **0.0914** |
| **Counterfactual Oracle** | Offline Diagnostic Bound | **85.0%** [78.0, 91.0] | +3.0% [+0.0, +7.0] | 0.0882 | 1,446 | 1.01x | 0 | 0.0000 |

*Note: Counterfactual Oracle is an offline counterfactual upper bound diagnostic computed from observed branch outcomes, NOT an executable deployment policy.*

---

## 4. Dataset-wise Breakdown (DocVQA vs ChartQA)

| Dataset Domain | Sample Size | Monolithic Acc | Original GVoC Acc | C-GVoC Acc | Offline Oracle Bound | Core Failure Mode |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **DocVQA (Text & Forms)** | 50 | **100.0%** | 94.0% | **100.0%** | **100.0%** | Text is readable; GVoC intervenes needlessly. C-GVoC stops correctly. |
| **ChartQA (Visual Reasoning)** | 50 | **64.0%** | 50.0% | **52.0%** | **70.0%** | Visual re-grounding crops out global axes, creating parsing errors. |

---

## 5. Phase 4 Uncertainty Proxy Verification Breakdown

- **Evaluated Action Branches:** 200 paired counterfactual evaluations across 100 unique documents.
- **Linear Association (Pearson $r$):** `-0.2173` (p = `0.0020`, Clustered 95% CI `[-0.3194, -0.1209]`).
- **Rank Association (Spearman $\rho$):** `-0.1861` (p = `0.0083`).
- **Binned Estimation Error ($\overline{\epsilon} = |\hat{\Delta} - \Delta^*|$):**
  - Low Dispersion ($\hat{\sigma} < 0.49$): `0.7084`
  - Mid Dispersion ($0.49 \le \hat{\sigma} \le 0.68$): `0.5182`
  - High Dispersion ($\hat{\sigma} > 0.68$): `0.5100`
- **Scientific Audit Finding:** The metric does not track epistemic uncertainty. Retaining the term "calibrated uncertainty" is unacceptable for submission.

---

## 6. Claims That Must Be Removed or Reconciled

1. **REMOVE:** "Reaches 70.2% accuracy across 16,000 queries" as an empirical live model finding.
   - **MANDATORY REPLACEMENT:** "Across an offline 16,000-query diagnostic benchmark simulation... In live empirical evaluation on held-out document tasks (Mistral Pixtral-12B)..."
2. **REMOVE:** Claims of "calibrated epistemic uncertainty" or "statistical standard errors".
   - **MANDATORY REPLACEMENT:** "Heuristic observation-space telemetry dispersion penalty".
3. **REMOVE:** Claims that visual interventions universally improve VLM performance.
   - **MANDATORY REPLACEMENT:** Acknowledge that on clean, unoccluded documents, forcing test-time interventions causes Type-I errors, and conservative regularizers are essential to prevent model degradation.

---

## 7. Strategic Submission Recommendation

### Recommendation: **DO NOT SUBMIT TO NAACL IN CURRENT FORM**
1. The paper was structured around an empirical victory (+57 points) that was entirely an artifact of offline heuristic simulation.
2. In reality, modern VLMs are already strong in monolithic zero-shot mode on standard benchmarks. GVoC's greedy ratio router creates false interventions that degrade performance.
3. **Paths Forward:**
   - **Path A (The Honest Pivot):** Reframe the paper from "Look Closer Beats Think Longer" to **"The Intervention Trap: Why Test-Time Visual Scaling Fails on Clear Documents and How Conservative Gating Mitigates Harm."**
   - **Path B (The Selective Setting):** Benchmark GVoC specifically on *heavily degraded / downsampled* document images (e.g., 72 DPI scans, severe blur, low-resolution crops) where monolithic inference genuinely fails ($< 20\%$) and optical zoom is physically necessary.
