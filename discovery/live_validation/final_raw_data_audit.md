# Final Live-Pilot Forensic Audit: Raw Evidence Verification and Reproducibility Report

**Audit Objective:** Independent forensic verification of the live real-world pilot evaluation (`discovery/live_validation/live_evaluation.db`) conducted on Mistral Pixtral-12B (`pixtral-12b-2409`), auditing model-call provenance, dataset sampling validity, metric recomputation, counterfactual oracle mechanics, uncertainty proxy validity, intervention failure mechanisms, and manuscript claims in `naacl/main.tex`.

**Auditor:** Empirical Research & Methodology Auditor  
**Date of Audit:** October 10, 2026  
**Final Audit Verdict:** **PARTIAL PASS**  
*(The live pilot raw data is genuine, complete, unmanipulated, and reproducible with zero mocks or synthetic fallbacks. However, the empirical results directly contradict the core thesis of GVoC and reveal that C-GVoC is an incomplete guardrail, requiring key statistical corrections and the retraction of several theoretical claims in the manuscript.)*

---

## 1. Model-Call Provenance and Allocation

### A. Raw API Call Accounting
We audited the raw SQLite table `live_api_calls` in `discovery/live_validation/live_evaluation.db`:
- **Total Executed API Calls:** Exactly **300 calls**.
- **Successful Calls:** **300** (`status = 'success'`).
- **Failed / Errored Calls:** **0**.
- **Retried Calls:** **0** (all completed on `attempt = 1`).
- **Model Endpoint:** 100% routed to Mistral AI official API (`provider = 'mistral'`, `model_id = 'pixtral-12b-2409'`).
- **Temporal Traceability:** All 300 calls executed sequentially on October 10, 2026 between 16:21:44 and 16:33:22 UTC. Total runtime: 697.7 seconds (~11.6 minutes).
- **Latency Distribution:** Mean latency 2.06s, minimum 0.81s, maximum 14.40s. Zero calls exhibited mock or cached latencies (<0.05s).
- **Token Accounting:** Total tokens consumed across 300 calls: 439,360 tokens. Mean tokens per call: 1,464. Prompt tokens ranged from 126 to 2,933, accurately reflecting variable high-resolution document image dimensions.
- **Mock / Synthetic Check:** Zero mocks, zero cached responses, zero synthetic answers, and zero silent fallbacks were present. Every single response originated from the live Mistral provider.

### B. Explanation of the 300 Calls vs. 5 Decision Policies
The live pilot evaluated five methods across 100 frozen benchmark instances:
1. `monolithic` (direct zero-shot inference at $s_0$)
2. `deterministic` (heuristic resolution/aspect-ratio routing)
3. `gvoc` (unregularized advantage routing with $\lambda = 0$)
4. `cgvoc` (conservative dispersion-penalized routing with $\lambda = 0.5$)
5. `oracle` (retrospective counterfactual optimum)

**Why does the database record exactly 300 API calls instead of $5 \times 100 = 500$ calls?**
The evaluation used a rigorous **pre-executed counterfactual action pool design**:
- For every instance $i \in \{1, \dots, 100\}$, the live runner executed the complete 3-branch counterfactual action space:
  1. `initial_inference` (Branch 1, $a = \text{stop}$): 100 calls.
  2. `reground` (Branch 2, $a = \text{reground}$): 100 calls.
  3. `reexec` (Branch 3, $a = \text{reexecute}$): 100 calls.
- Total external calls: $100 \text{ instances} \times 3 \text{ action branches} = \mathbf{300 \text{ calls}}$.
- Each of the 5 decision methods is an allocation policy that selects one of these three pre-executed branches for each instance.
- This design guarantees that every method is evaluated on **identical provider responses** without confounding stochastic API variations between methods.

### C. Instance-by-Method Completeness Matrix
We generated `discovery/live_validation/instance_method_completeness.csv` containing all 100 instances across all 5 methods (500 total episode outcomes):
- **Completeness:** 100.0% (500/500 non-null outcomes).
- **Duplicate Rows:** 0.
- **Missing Evaluations:** 0.

---

## 2. Dataset Validity, Instance Selection, and Generalization Scope

### A. Instance Selection Timing and Bias Audit
- **Preregistration Timing:** The 100 benchmark instances were frozen in `discovery/live_validation/pilot_dataset/preregistered_100.json` before live execution began.
- **Sampling Mechanism:** Selection was **deterministic sequential prefix sampling** (`offset=0&limit=50` from Hugging Face dataset splits), **NOT random sampling**.
- **Ordering Bias:** Taking the first 50 instances from Hugging Face introduces substantial document-clustering bias:
  - In DocVQA, the 50 queries correspond to only **19 unique document scans** (e.g., one single multi-page industrial report contains 8 evaluated questions).
  - In ChartQA, the 50 queries correspond to only **25 unique chart images**.
  - **Effective Sample Size:** The effective independent visual sample size is $N_{\text{images}} = \mathbf{44}$, not 100.

### B. Ground Truth and Scoring Verification
- **Source Integrity:** Verified against official datasets (`lmms-lab/DocVQA` validation split and `HuggingFaceM4/ChartQA` test split). All image hashes, question strings, and ground truth lists match the source datasets.
- **Scoring Function:** Evaluated via `discovery/live_validation/scoring.py`:
  - DocVQA: Evaluated via case/punctuation-insensitive exact match and token F1, consistent with the official DocVQA benchmark protocol.
  - ChartQA: Evaluated via relaxed accuracy (accepting numeric predictions within 5% relative tolerance), adhering to Masry et al. (2022).

### C. Aggregation Validity and Population Generalization Scope
DocVQA and ChartQA exhibit fundamentally divergent behavior under Mistral Pixtral-12B:
- On DocVQA, monolithic direct inference already achieves **100.0% accuracy** on this 50-query prefix. There is a total ceiling effect.
- On ChartQA, monolithic direct inference achieves **64.0% accuracy**, while intervention degrades accuracy to **50.0%–52.0%**.
- **Aggregation Hazard:** Aggregating these two datasets into a single "Overall" metric obscures the fact that the intervention policy is tested on two extreme regimes (a saturated ceiling regime where any intervention is harmful, and a complex reasoning regime where interventions cause prompt truncation).
- **Generalization Scope Artifact:** These pilot results generalize specifically to:
  *High-resolution, clean document and chart images processed by modern large-window vision-language models (e.g., Pixtral-12B) where downsampling information loss is minimal.* They do **not** generalize to severely downsampled, blurry, or occluded documents where visual information is genuinely destroyed.

---

## 3. Recomputed Primary Outcomes

All primary metrics were recomputed from raw database records using `discovery/live_validation/audit_scripts/recompute_primary_outcomes.py` and exported to `discovery/live_validation/recomputed_metrics.csv`.

### Recomputed Outcome Table

| Subset | Method | Accuracy (95% Wilson CI) | Paired Diff vs. Mono (95% Boot CI) | Discordant Pairs ($n_{10}, n_{01}$) | McNemar Exact $p$ | Bootstrap Paired $p$ | Mean Tokens (Cost Ratio) | Intervention Rate | False Interventions | Norm. Regret |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Overall** ($N=100$) | **Monolithic** | 82.0% [73.3, 88.3] | Baseline (0.0%) | (0, 0) | 1.0000 | 1.0000 | 1,428 (1.00x) | 0.0% | 0 | 0.0300 |
| | **Deterministic** | 79.0% [70.0, 85.8] | -3.0% [-7.0, 0.0] | (3, 0) | 0.2500 | 0.0954 | 1,566 (1.10x) | 15.0% | 3 | 0.0608 |
| | **GVoC ($\lambda=0$)** | **72.0%** [62.5, 79.9] | **-10.0%** [-17.0, -3.0] | **(12, 2)** | **0.0129** | **0.0046** | 2,889 (**2.02x**) | 100.0% | 12 | 0.1409 |
| | **C-GVoC ($\lambda=0.5$)** | **76.0%** [66.8, 83.3] | **-6.0%** [-13.0, 0.0] | **(9, 3)** | **0.1460** | **0.0956** | 1,676 (1.17x) | 48.0% | 9 | 0.0914 |
| | **Oracle (Bound)** | 85.0% [76.7, 90.7] | +3.0% [0.0, 7.0] | (0, 3) | 0.2500 | 0.0882 | 1,446 (1.01x) | 3.0% | 0 | 0.0000 |
| **DocVQA** ($N=50$) | **Monolithic** | 100.0% [92.9, 100.0] | Baseline (0.0%) | (0, 0) | 1.0000 | 1.0000 | 2,389 (1.00x) | 0.0% | 0 | 0.0000 |
| | **Deterministic** | 98.0% [89.5, 99.6] | -2.0% [-6.0, 0.0] | (1, 0) | 1.0000 | 0.7372 | 2,536 (1.06x) | 6.0% | 1 | 0.0208 |
| | **GVoC ($\lambda=0$)** | 94.0% [83.8, 97.9] | -6.0% [-14.0, 0.0] | (3, 0) | 0.2500 | 0.1004 | 4,800 (2.01x) | 100.0% | 3 | 0.0788 |
| | **C-GVoC ($\lambda=0.5$)** | 100.0% [92.9, 100.0] | 0.0% [0.0, 0.0] | (0, 0) | 1.0000 | 1.0000 | 2,389 (1.00x) | 0.0% | 0 | 0.0000 |
| | **Oracle (Bound)** | 100.0% [92.9, 100.0] | 0.0% [0.0, 0.0] | (0, 0) | 1.0000 | 1.0000 | 2,389 (1.00x) | 0.0% | 0 | 0.0000 |
| **ChartQA** ($N=50$) | **Monolithic** | 64.0% [50.1, 75.9] | Baseline (0.0%) | (0, 0) | 1.0000 | 1.0000 | 467 (1.00x) | 0.0% | 0 | 0.0600 |
| | **Deterministic** | 60.0% [46.2, 72.4] | -4.0% [-10.0, 0.0] | (2, 0) | 0.5000 | 0.2622 | 597 (1.28x) | 24.0% | 2 | 0.1008 |
| | **GVoC ($\lambda=0$)** | 50.0% [36.6, 63.4] | -14.0% [-26.0, -2.0] | (9, 2) | 0.0654 | 0.0354 | 978 (2.09x) | 100.0% | 9 | 0.2030 |
| | **C-GVoC ($\lambda=0.5$)** | 52.0% [38.5, 65.2] | -12.0% [-26.0, 0.0] | (9, 3) | 0.1460 | 0.0984 | 963 (2.06x) | 96.0% | 9 | 0.1829 |
| | **Oracle (Bound)** | 70.0% [56.2, 80.9] | +6.0% [0.0, 14.0] | (0, 3) | 0.2500 | 0.0938 | 504 (1.08x) | 6.0% | 0 | 0.0000 |

### Statistical Significance and $p$-Value Audit
- **Reported $p = 0.0046$ (GVoC vs. Monolithic):**
  - **Source Test:** Two-sided paired bootstrap difference test ($N=10,000$ resamples of document instances).
  - **Null Hypothesis:** $H_0: \mathbb{E}[Y_{\text{GVoC}} - Y_{\text{Monolithic}}] = 0$.
  - **Exact McNemar Test:** $n_{10} = 12, n_{01} = 2 \implies p = \mathbf{0.0129}$.
  - **Conclusion:** Both tests confirm that unregularized GVoC causes a **statistically significant degradation in accuracy** ($p < 0.05$) while burning double the compute (+102% tokens).
- **Reported $p = 0.0956$ (C-GVoC vs. Monolithic):**
  - **Source Test:** Two-sided paired bootstrap difference test ($N=10,000$ resamples).
  - **Exact McNemar Test:** $n_{10} = 9, n_{01} = 3 \implies p = \mathbf{0.1460}$.
  - **Correction:** The difference (-6.0 points) is not statistically significant at the $\alpha = 0.05$ level, but **does NOT demonstrate parity or preservation of accuracy**. The statistical power is limited ($N=100$), and the point estimate shows net harm (9 harmful flips vs. 3 rescues).

---

## 4. Counterfactual Oracle and Intervention Labels Audit

### A. Oracle Definition and Epistemic Status
- **Retrospective Construction:** The Counterfactual Oracle selects $a^*(i) = \arg\min_{a \in \mathcal{A}} \text{Loss}(i, a)$ using the ground-truth outcome $Y_i(a)$ observed *after* inference has already taken place.
- **Diagnostic Upper Bound:** The Oracle is an **offline diagnostic upper bound**, not a deployable policy. It represents the theoretical maximum accuracy achievable under this action set if an agent had supernatural foresight.
- **Zero Regret by Construction:** Oracle regret is defined as $\mathcal{R}(\pi) = \mathbb{E}[\text{Loss}(\pi(s)) - \min_a \text{Loss}(a)]$. Thus, Oracle regret is **zero by mathematical identity**.

### B. False Intervention Operational Definition
- We audited the operational definition of "false intervention":
  $$\text{False Intervention}(i, \pi) \iff \pi(s_i) \ne \text{stop} \quad \text{AND} \quad Y_i(\text{stop}) = 1 \quad \text{AND} \quad Y_i(\pi(s_i)) \le Y_i(\text{stop})$$
- This definition is **objective, non-circular, and controller-independent**. It measures whether the agent paid extra compute to disrupt an already-correct baseline answer.

---

## 5. Uncertainty Proxy Audit: Statistical Refutation

We cross-referenced `discovery/live_validation/uncertainty_reanalysis.md`:
- **Sample:** $N = 200$ evaluated counterfactual branches across 100 unique documents.
- **Pearson Correlation with Absolute Error:** $r = \mathbf{-0.2173} \quad (p = 0.0020), \quad 95\% \text{ Clustered CI: } [-0.3173, -0.1186]$.
- **Spearman Rank Correlation:** $\rho = \mathbf{-0.1861} \quad (p = 0.0083), \quad 95\% \text{ Clustered CI: } [-0.3075, -0.0706]$.
- **Binned Tertile Error:** Low dispersion instances ($\hat{\sigma} \le 0.49$) suffered MAE of **0.7084**, whereas high dispersion instances ($\hat{\sigma} > 0.68$) had MAE of **0.5100**.
- **Predictive Power:** $R^2 = 0.0472$ vs. a constant baseline.
- **Scientific Verdict:** The dispersion proxy $\hat{\sigma}_a(s)$ is **negatively correlated with true prediction error**. It cannot be described as an epistemic uncertainty estimator or a calibrated risk bound. It functions as an uncalibrated empirical heuristic.

---

## 6. Intervention Mechanics on Charts: Refuting the Crop Loss Narrative

We cross-referenced `discovery/live_validation/intervention_case_studies.md`:
- **The "Cropping Loss" Myth:** Prior drafts claimed that visual re-grounding degrades charts because cropping cuts off axes, legends, or units.
- **Raw Evidence:** In `live_runner.py`, `image_path = img_path` was passed to all calls. **Zero spatial cropping or coordinate cropping occurred.**
- **Actual Failure Mechanisms:**
  1. **Prompt-Induced Verbosity vs. Token Ceiling:** Prompts requesting "high precision" or "step-by-step logic" shifted generation from concise numerical answers to multi-sentence explanatory narratives. At `max_tokens=60` (`reground`) and `max_tokens=80` (`reexec`), generation was truncated before outputting the final number in 8 of the 9 failures (`chartqa_001`, `chartqa_009`, `chartqa_011`, `chartqa_014`, `chartqa_022`, `chartqa_027`, `chartqa_039`).
  2. **Calculation Drift:** In `chartqa_041`, verbose verification caused the model to misidentify comparative segments that single-pass inference had solved correctly.
- **Manuscript Correction:** All text attributing chart degradation to "loss of axes from cropping" must be removed.

---

## 7. Manuscript Integrity Audit (`naacl/main.tex`)

We conducted a line-by-line audit of `naacl/main.tex` against the verified raw data:

| Section & Line | Current Manuscript Claim | Raw Empirical Reality | Required Revision |
| :--- | :--- | :--- | :--- |
| **Abstract (line 40)** | "C-GVoC reliably suppresses false interventions to preserve optimal stopping accuracy with zero cost overhead." | In reality, C-GVoC overall accuracy is **76.0%** (vs. 82.0% monolithic), and on ChartQA it drops to **52.0%** (vs. 64.0% monolithic) with **+17% to +106% cost overhead**. | **WITHDRAW CLAIM.** State that C-GVoC partially reduces false interventions compared to unregularized GVoC, but still causes net harm on charts. |
| **Abstract & Sec 4.1** | 16,000-query benchmark | Verified as an offline synthetic simulation. | Maintained: already labeled as simulation in main text. |
| **Section 3.2 (p. 2)** | Uncertainty formulation labeled as "Calibrated Epistemic Uncertainty" with PAC/LCB guarantees | Proxy is negatively correlated with error ($r = -0.2173$); no PAC guarantee holds. | **WITHDRAW THEORETICAL CLAIMS.** Relabel strictly as an empirical dispersion heuristic. |
| **Table 1 (p. 1)** | 16,000 simulation results presented without live empirical pilot table | Reviewers cannot see the live 100-instance pilot results in the main tables. | Insert a concise live evaluation table or paragraph reporting actual Pixtral-12B outcomes. |
| **Conclusion (line 176)** | "maintaining optimal stopping accuracy." | Contradicted by 9 harmful flips on ChartQA. | **REVISE.** Acknowledge prompt-induced verbosity truncation and domain-specific intervention risks. |

---

## 8. Final Audit Synthesis and Verdict

### A. Four-Way Categorical Separation

#### 1. Verified Facts
- Exactly 300 genuine API calls were executed on Mistral Pixtral-12B with zero mocks, failures, or synthetic fallbacks.
- Monolithic direct inference is extremely strong on clean documents (82.0% overall, 100.0% on DocVQA, 64.0% on ChartQA).
- Unregularized GVoC ($\lambda = 0$) causes severe over-intervention (100% intervention rate), cutting accuracy to 72.0% ($p = 0.0129$) while doubling token cost (+102%).
- No image cropping was performed during the live pilot; all calls received the full original image.

#### 2. Corrected Calculations
- C-GVoC paired difference vs. Monolithic: $-6.0\%$ (McNemar exact $p = 0.1460$, bootstrap $p = 0.0956$).
- GVoC paired difference vs. Monolithic: $-10.0\%$ (McNemar exact $p = 0.0129$, bootstrap $p = 0.0046$).
- Dispersion proxy correlation with absolute error: $r = -0.2173$ ($p = 0.0020$), Spearman $\rho = -0.1861$ ($p = 0.0083$).
- Effective independent visual document sample size: $N_{\text{images}} = 44$.

#### 3. Plausible but Unverified Explanations
- The hypothesis that higher `max_tokens` (e.g., 256 tokens) would rescue the 8 truncated ChartQA instances is plausible and supported by response transcripts, but has not been tested in live API inference.
- The hypothesis that visual cropping *would* fail on charts due to coordinate loss remains a theoretical intuition, not an observed empirical fact of this pilot.

#### 4. Claims That Must Be Withdrawn
- **WITHDRAW:** Any claim that C-GVoC "preserves optimal stopping accuracy" or has "zero cost overhead."
- **WITHDRAW:** Any claim that $\hat{\sigma}_a(s)$ provides "calibrated epistemic uncertainty" or theoretical LCB risk bounds.
- **WITHDRAW:** Any claim that chart failures were caused by physical image cropping.

---

### B. Final Audit Verdict

$$\mathbf{VERDICT: \quad PARTIAL \quad PASS}$$

**Justification:**  
The raw experimental artifacts, database records, and execution code are **100% genuine, traceable, and reproducible**. There is zero fabrication, mock data, or synthetic leakage in the live pilot.  
However, the pilot passes only with **mandatory corrections**: the manuscript's claims regarding C-GVoC's accuracy preservation, uncertainty calibration, and crop failure mechanics are directly contradicted by the raw data and must be revised prior to paper submission.

---

## 9. Reproducibility Guide: Exact Commands to Regenerate All Artifacts

To regenerate every audit artifact from scratch using the raw frozen database (`live_evaluation.db`):

```bash
# 1. Regenerate Instance-by-Method Completeness Matrix (Section 1)
python discovery/live_validation/audit_scripts/generate_completeness_matrix.py

# 2. Recompute Primary Outcomes, CIs, Discordant Pairs, and Regret (Section 3)
python discovery/live_validation/audit_scripts/recompute_primary_outcomes.py

# 3. Recompute Uncertainty Proxy Correlations and Tertile Binning (Section 5)
python discovery/live_validation/audit_scripts/audit_uncertainty_proxy.py

# 4. Extract Forensic ChartQA Harmful Flip Case Studies (Section 6)
python discovery/live_validation/audit_scripts/export_chartqa_harmful.py

# 5. Run Regret Bound and Loss Unit Tests
pytest discovery/live_validation/test_regret_bounds.py
```
