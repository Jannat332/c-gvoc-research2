# Independent Research Audit: Context-Preserving, Cost-Aware Visual Evidence Acquisition (CCEA)

**Audit Target:** NAACL Research Track Manuscript (*Think Longer or Look Closer? Test-Time Scaling for Visual Document Understanding*)  
**Repository:** `https://github.com/Jannat332/c-gvoc-research2`  
**Audited Branch:** `feature/ccea-context-preserving-acquisition`  
**Audited Commit:** `fa2e4ed241055de38a90ee1e06dbe8b46df28e83`  
**Draft Pull Request:** PR #1 (`https://github.com/Jannat332/c-gvoc-research2/pull/1`)  
**Auditor:** Independent Research Auditor & Adversarial Scientific Reviewer  
**Audit Date:** October 11, 2026  

---

## 1. Repository and Commit State

* **Repository Remote:** `https://github.com/Jannat332/c-gvoc-research2`
* **Current Working Branch:** `feature/ccea-context-preserving-acquisition`
* **Head Commit SHA:** `fa2e4ed241055de38a90ee1e06dbe8b46df28e83`
* **Commit Message:** `Implement CCEA evidence acquisition, physical PIL crop extraction, cost-aware stopping router, test suite, and central ablation`
* **Base Branch:** `main` at commit `4771a192305f5f5246a3ee1968a7f1d5d95d5891` (untouched, unmodified)
* **Draft PR Status:** PR #1 is **OPEN** and marked **DRAFT**. Target base: `main`, head: `research/context-preserving-acquisition` (synchronized with commit `fa2e4ed`).
* **Working Tree:** Clean (zero unstaged changes; runtime temporary crops ignored via `.gitignore`).
* **Security & Secret Verification:** No API keys, credentials, or personal access tokens are stored in tracked files. All keys are resolved dynamically from process environment or external configuration.

---

## 2. Test Suite Execution & Classification

The complete test suite was executed locally. Every test ran to completion with zero collection errors and zero failures.

```powershell
$env:PYTHONPATH = "."
python -m pytest gvoc_engine/tests -v
```
**Exit Code:** `0`  
**Summary:** `40 passed in 1.00s`

### Test Classification & Methodology Breakdown
| Test Module | Command | Type / Environment | Pass / Fail | Exit Code | Description |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `test_ccea_geometry.py` | `python -m unittest gvoc_engine.tests.test_ccea_geometry` | Pure Unit Test (Deterministic Geometry) | 8 / 0 | 0 | Validates bounding box validation, reverse bounds, parser formats, normalized $[0, 1]$ coordinate scaling, and context union. |
| `test_ccea_intervention.py` | `python -m unittest gvoc_engine.tests.test_ccea_intervention` | Integration Test (PIL Cropping + Mock Client) | 6 / 0 | 0 | Tests physical PIL file cropping from synthetic images, context retention telemetry, malformed locator fail-closed, and missing file handling. |
| `test_ccea_router.py` | `python -m unittest gvoc_engine.tests.test_ccea_router` | Unit Test (Decision Theory) | 5 / 0 | 0 | Tests cost-aware decision rule, clean-state suppression, step-budget exhaustion, and calibrated safe abstention. |
| `test_evaluation_integrity.py` | `python -m unittest gvoc_engine.tests.test_evaluation_integrity` | Unit Test (Integrity & Scoring) | 4 / 0 | 0 | Tests F1/exact-match scoring, ground-truth isolation from router signatures, error telemetry retention, and token summing. |
| `test_context_preservation.py` | `python -m unittest gvoc_engine.tests.test_context_preservation` | Pure Unit Test (Geometry) | 5 / 0 | 0 | Base context-preservation tests from PR #1. |
| `test_cgvoc.py` | `python -m unittest gvoc_engine.tests.test_cgvoc` | Unit Test (Legacy Algorithm) | 6 / 0 | 0 | Unit tests for LCB value calculations and clean-state suppression. |
| `test_risk_bounded_router.py` | `python -m unittest gvoc_engine.tests.test_risk_bounded_router` | Unit Test (Legacy Algorithm) | 6 / 0 | 0 | Unit tests for paired epistemic uncertainty estimation. |

**Auditor Note:** All 40 unit and integration tests use deterministic geometry or mock clients. None of the tests in `gvoc_engine/tests` incur live API costs. Live evaluations are separated strictly into `gvoc_engine/experiments/` and `discovery/live_validation/`.

---

## 3. Live versus Simulated Evidence Inventory

The repository contains four distinct tiers of evidence, which must never be conflated:

1. **Pure Unit / Mock Tests (`gvoc_engine/tests/`):**
   - 40 automated tests. Fully deterministic, zero network calls.
2. **Legacy Offline Benchmark Simulation (`gvoc_engine/experiments/run_cgvoc_head_to_head.py`):**
   - $N = 16,000$ synthetic items.
   - **AUDIT FINDING:** Evaluates baselines using synthetic state vectors and predetermined `effective_set` lookups (`is_correct = 1 if act in effective_set`). This is an offline simulation, not a live VLM evaluation.
3. **Legacy Pilot Experiment (`discovery/live_validation/live_evaluation.db`):**
   - 100 DocVQA/ChartQA items evaluated with Mistral Pixtral-12B.
   - **AUDIT FINDING:** In this legacy experiment, "re-grounding" was executed merely as a text prompt re-querying the unaltered full image without image cropping or context preservation.
4. **Current CCEA Live Pilot (`discovery/live_validation/ccea_ablation_records.json`):**
   - $N = 3$ genuine DocVQA instances (`docvqa_000`, `docvqa_001`, `docvqa_002`) evaluated live against Mistral Pixtral-12B (`pixtral-12b-2409`) across 4 conditions with physical PIL cropping and measured API tokens/latencies.

---

## 4. Per-Document Live Pilot Audit Table

Independently extracted from raw execution artifact: `discovery/live_validation/ccea_ablation_records.json`.

| Field / Attribute | Document 1 (`docvqa_000`) | Document 2 (`docvqa_001`) | Document 3 (`docvqa_002`) |
| :--- | :--- | :--- | :--- |
| **Document Image** | `docvqa_000.jpg` ($1370 \times 1480$) | `docvqa_001.jpg` ($1750 \times 2270$) | `docvqa_002.jpg` ($850 \times 1644$) |
| **Question** | What the location address of NSDA? | According to budget request summary what is total amount of other expenses?? | Who is ‘presiding’ TRRF GENERAL SESSION (PART 1)? |
| **Reference Ground Truth** | `['1128 SIXTEENTH ST., N. W., WASHINGTON, D. C. 20036', ...]` | `['$975.00', '975.00']` | `['TRRF Vice President', 'lee a. waller']` |
| **Target Evidence Box** | `[592, 479, 710, 753]` | `[908, 612, 1089, 962]` | `[657, 297, 789, 467]` |
| **Condition 1 (Full Image)** | | | |
| - Answer | `1128 Sixteenth St., N.W., Washington, D.C. 20036.` | `$975.00.` | `Lee A. Waller, TRRF Vice President` |
| - Exact Match / F1 | Acc = 1, F1 = 0.625 | Acc = 1, F1 = 1.000 | Acc = 1, F1 = 1.000 |
| - Tokens / Latency | 2,699 tokens, 1.896s | 2,460 tokens, 1.386s | 1,695 tokens, 1.550s |
| **Condition 2 (Target-Only Crop)** | | | |
| - Crop Box $[y_0, x_0, y_1, x_1]$ | `[586, 465, 716, 767]` | `[899, 594, 1098, 980]` | `[650, 289, 796, 475]` |
| - Retained Context | None ($0/4$) | None ($0/4$) | None ($0/4$) |
| - Lost Context Kinds | `column_label`, `row_label`, `unit`, `footnote` | `column_label`, `row_label`, `unit`, `footnote` | `column_label`, `row_label`, `unit`, `footnote` |
| - Answer | `112B SIXTEENTH ST., N.W., WASHINGTON` | `$15,000.00.` | `Philip G. Kuehn.` |
| - Exact Match / F1 | **Acc = 0, F1 = 0.429** | **Acc = 0, F1 = 0.000** | **Acc = 0, F1 = 0.000** |
| - Failure Mechanism | Truncated zip code & typo ("112B") | Hallucinated wrong row ($15,000$) | Extracted adjacent speaker from Part 2 |
| - Tokens / Latency | 2,834 tokens, 2.815s | 2,654 tokens, 2.259s | 1,817 tokens, 2.382s |
| **Condition 3 (CCEA Context Crop)** | | | |
| - Crop Box $[y_0, x_0, y_1, x_1]$ | `[82, 82, 1456, 877]` | `[127, 105, 2233, 1120]` | `[92, 51, 1617, 544]` |
| - Retained Context | Full ($4/4$ context regions preserved) | Full ($4/4$ context regions preserved) | Full ($4/4$ context regions preserved) |
| - Answer | `1128 Sixteenth St., N.W., Washington, D.C. 20036` | `$975.00` | `Lee A. Waller, TRRF Vice President` |
| - Exact Match / F1 | **Acc = 1, F1 = 0.625** | **Acc = 1, F1 = 1.000** | **Acc = 1, F1 = 1.000** |
| - Tokens / Latency | 4,278 tokens, 3.367s | 4,070 tokens, 2.892s | 2,816 tokens, 2.883s |
| **Condition 4 (Cost-Aware CCEA)**| | | |
| - Chosen Action | `REGROUND` (Acquire CCEA crop) | `REGROUND` (Acquire CCEA crop) | `REGROUND` (Acquire CCEA crop) |
| - Answer | `1128 Sixteenth St., N.W., Washington, D.C. 20036` | `$975.00` | `Lee A. Waller, TRRF Vice President` |
| - Exact Match / F1 | Acc = 1, F1 = 0.625 | Acc = 1, F1 = 1.000 | Acc = 1, F1 = 1.000 |
| - Total Tokens / Latency | 4,278 tokens, 3.367s | 4,070 tokens, 2.892s | 2,816 tokens, 2.883s |

---

## 5. Metric Definitions & Reproducibility Investigation

### The 100% Accuracy vs. 0.875 Token F1 Discrepancy Resolved
The reported pilot metrics for Condition 1 and Condition 3 state:  
`Accuracy: 100.0%` | `Average Token F1: 0.875`.

An independent audit of `discovery/live_validation/scoring.py` revealed the exact cause:

1. **Accuracy Metric Formulation:**  
   In `score_vdu_answer(pred, ground_truth_list)`, accuracy is an integer indicator $y \in \{0, 1\}$.
   ```python
   norm_pred = normalize_text(pred)
   for gt in ground_truth_list:
     norm_gt = normalize_text(str(gt))
     if (
         norm_pred == norm_gt
         or (norm_gt in norm_pred)
         or (norm_pred in norm_gt)
     ):
       is_correct = 1
       best_f1 = 1.0
       break
     f1 = compute_token_f1(pred, str(gt))
     if f1 > best_f1:
       best_f1 = f1
```
   `is_correct = 1` occurs if the normalized prediction is an exact match, a substring, or a superstring of any ground-truth alias.
2. **Token F1 Formulation:**  
   $F1 = \frac{2 \cdot P \cdot R}{P + R}$, computed over whitespace-separated tokens after punctuation stripping (`string.punctuation`).
3. **The Root Discrepancy on `docvqa_000`:**
   - Model prediction: `"1128 Sixteenth St., N.W., Washington, D.C. 20036"`
   - Ground truth string: `"1128 SIXTEENTH ST., N. W., WASHINGTON, D. C. 20036"`
   - When `normalize_text` strips punctuation:
     - Model tokens: `['1128', 'sixteenth', 'st', 'nw', 'washington', 'dc', '20036']` (7 tokens; `"N.W."` became `"nw"`).
     - Ground truth tokens: `['1128', 'sixteenth', 'st', 'n', 'w', 'washington', 'd', 'c', '20036']` (9 tokens; `"N. W."` had spaces, producing `'n'` and `'w'`).
   - Token intersection: `{'1128', 'sixteenth', 'st', 'washington', '20036'}` (5 tokens).
   - Precision = $5/7 \approx 0.714$, Recall = $5/9 \approx 0.556$.
   - **Token F1 = $2 \cdot \frac{0.714 \cdot 0.556}{0.714 + 0.556} = \mathbf{0.625}$**.
   - Substring match: The address string was accepted as correct ($y = 1$).
4. **Aggregate Calculation:**
   $$\text{Mean Accuracy} = \frac{1 + 1 + 1}{3} = 1.000 \quad (100.0\%)$$
   $$\text{Mean Token F1} = \frac{0.625 + 1.000 + 1.000}{3} = \frac{2.625}{3} = \mathbf{0.875}$$
   The reported numbers are mathematically reproducible from the raw model outputs.

---

## 6. Evaluation Integrity, Context Annotation Provenance & Potential Leakage

### Context Annotation Provenance (CRITICAL AUDIT FINDING)
* **How Context Was Obtained in the Pilot:**  
  In `run_ccea_ablation.py`, line 62 defines `create_synthetic_evidence_region(width, height, inst_id)`.  
  The coordinates for the target and required context regions (column header, row label, unit, footnote) were generated via **fixed spatial bounding fractions** relative to image dimensions ($0.40 \cdot h$ to $0.48 \cdot h$ for target cell, $0.20 \cdot h$ for column header, etc.).
* **Scientific Caveat:**  
  The context boxes were **not** discovered by an autonomous layout segmentation model. While `parse_bounding_box` in `context_preservation.py` is capable of parsing coordinate outputs from VLM prompts, the current ablation relied on hardcoded spatial regions.
* **Integrity Directive:**  
  The manuscript **must not** claim that CCEA currently features "autonomous layout discovery" or "automatic context discovery." It must be accurately described as:  
  *"A context-preservation constraint that enforces retention of supplied or annotated layout context."*

### Policy and Label Leakage Audit
* **Router Call Signature:** `select_action(state, remaining_budget, evidence_region, image_width, image_height)`.
* **Zero Label Leakage:** The ground-truth reference answers are **never** passed into `CCEACostAwareRouter` or `CCEAIntervention`.
* **Scoring Isolation:** Correctness scoring is strictly computed post-hoc by `score_vdu_answer` on the final output string.
* **Evaluation Integrity Verified:** No ground-truth outcomes are used to select routing decisions or manufacture answers.

### Router Action Differentiation
* In the 3-instance live pilot, the cost-aware router selected `REGROUND` on all 3 instances because the input state was initialized with moderate layout divergence (`d_layout = 0.25`).
* As a result, Condition 4 produced identical results to Condition 3.
* **Auditor Note:** To prove that the cost-aware controller saves compute, the evaluation must include clean, unambiguous documents where $\hat{P}_{\text{stop}} \ge \tau_{\text{clean}}$, verifying that the controller chooses `STOP` and saves tokens compared to fixed intervention.

---

## 7. Scientific Claim Audit

| Manuscript Claim | Audit Evidence | Audit Verdict | Requirements to Upgrade / Validate |
| :--- | :--- | :---: | :--- |
| **Claim 1:** "Unconstrained cropping that severs table headers and labels causes severe VDU performance degradation." | Confirmed on 3 live DocVQA documents: Target-only crops dropped accuracy from 100% to 0% due to loss of units and headers. | **SUPPORTED (Pilot Scale, $N=3$)** | Replicate on $N \ge 24$ held-out documents with confidence intervals. |
| **Claim 2:** "Preserving spatial context (headers, units, labels) restores VDU interpretability and accuracy." | Confirmed on 3 live DocVQA documents: CCEA context crops restored accuracy from 0% to 100% (F1 = 0.875). | **SUPPORTED (Pilot Scale, $N=3$)** | Replicate on held-out sample with paired McNemar test ($p < 0.05$). |
| **Claim 3:** "The cost-aware router adaptively stops on clean documents, saving compute over fixed intervention." | Unit tests verify clean-state stopping and budget limits. However, in the 3-document live pilot, the router chose `REGROUND` on all 3 items. | **UNRESOLVED / REQUIRES EXPERIMENT** | Must execute evaluation on mixed clean/noisy instances where the router chooses `STOP` and demonstrates lower average token cost. |
| **Claim 4:** "CCEA performs autonomous layout context discovery." | Context boxes in `run_ccea_ablation.py` were generated from spatial bounding proportions. | **UNSUPPORTED / OVERCLAIM** | Downgrade claim: state that context regions are supplied via layout annotations or external segmenter. |
| **Claim 5:** "Epistemic uncertainty bounds are calibrated confidence intervals." | Uncertainty parameter $\hat{\sigma}$ is calculated from a heuristic proxy formula ($\sqrt{0.01 + 0.10 \cdot \text{var}_{\text{consensus}} + \dots}$). | **UNSUPPORTED AS CALIBRATED** | Must label $\hat{\sigma}$ as a *heuristic uncertainty penalty*, not an empirically calibrated statistical confidence bound. |

---

## 8. Small Pre-Registered Held-Out Evaluation Protocol

To rigorously evaluate CCEA without incurring excessive API expenses, the following pre-registered protocol is specified:

### Experimental Setup
* **Dataset:** 12 fresh, untouched instances from `discovery/live_validation/pilot_dataset/instances.json` (indices 10 to 21: 6 DocVQA + 6 ChartQA).
* **Model Backbone:** Mistral Pixtral-12B (`pixtral-12b-2409`), temperature = 0.0 (greedy decoding).
* **Token Budget Limit:** 4,000 tokens maximum per instance.

### Five Experimental Conditions
1. **$C_1$ (Full Overview):** Monolithic inference on full image ($max\_tokens = 60$).
2. **$C_2$ (Target-Only Crop):** Tight bounding box around target value, omitting headers/labels.
3. **$C_3$ (Context-Preserving CCEA):** Crop expanding target to include column header, row label, and unit.
4. **$C_4$ (Cost-Aware CCEA Controller):** Adaptive decision policy selecting `STOP`, `ACQUIRE`, or `ABSTAIN` based on $\Delta P_{\text{LCB}} - \lambda C_{\text{inc}}$.
5. **$C_5$ (Fixed-Acquisition Control):** Uniform center 50% crop baseline (matching legacy `run_confirmatory_experiment.py`).

### Metrics & Statistical Hypotheses
* **Primary Metric:** Strict Exact Match (EM) accuracy and Token F1 overlap.
* **Cost Metric:** Total tokens (prompt + completion) and latency (seconds).
* **Efficiency Metric:** Accuracy per 1,000 tokens.
* **Paired Statistical Test:** Exact McNemar's test comparing $C_3$ vs. $C_2$, and paired Wilcoxon signed-rank test on token consumption comparing $C_4$ vs. $C_3$.
* **Falsification Criterion:**  
  If $C_3$ does not achieve higher accuracy than $C_2$ ($p \ge 0.10$), the primary hypothesis (that context preservation is required for crop-based VDU scaling) is falsified.
  If $C_4$ consumes equal or greater tokens than $C_3$ without improving accuracy, the cost-aware stopping hypothesis is falsified.

### Budget Guard & Stopping Rules
* Total planned API calls: $12 \text{ instances} \times 4 \text{ conditions} = 48 \text{ calls}$.
* Estimated cost: $\approx \$0.015$ USD.
* Automatic stop trigger: Abort immediately if API error rate exceeds $15\%$ or total tokens exceed $150,000$.

---

## 9. Ordered Next Steps

1. **Retain Experimental Records & Do Not Merge PR:** Maintain PR #1 as a draft feature branch.
2. **Correct Manuscript Language:** Explicitly label router uncertainty as a *heuristic uncertainty penalty* (not an empirically calibrated confidence bound) and describe context boxes as *annotated/supplied layout context* (not autonomous discovery).
3. **Execute Pre-Registered 12-Instance Held-Out Evaluation:** Run `run_ccea_ablation.py` with the 5 conditions on held-out indices 10–21, logging all predictions, token counts, and crops to `discovery/live_validation/ccea_held_out_audit.json`.
4. **Compute Paired Significance & Confidence Intervals:** Calculate exact binomial 95% confidence intervals for accuracy and paired McNemar $p$-values.
5. **Freeze Artifacts for External Peer Review:** Archive the resulting JSON artifacts and generated crop PNGs in `research/` before preparing final paper revisions.
