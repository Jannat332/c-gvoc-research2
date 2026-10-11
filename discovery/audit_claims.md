# Phase 1 & 2 Forensic Audit: Claims vs. Empirical Evidence

**Auditors:**
1. **Empirical Methodology Auditor:** Experimental validity, sampling, causal attribution, and statistical limits.
2. **ML Systems Engineer:** Exact API payloads, image inputs, model settings, output limits, and provider metadata.
3. **Critical Paper Reviewer:** Scientific defensibility, benchmark comparisons, and novelty verification.

**Date:** October 10, 2026  
**Artifact Scope:** 100-Instance Live Pilot (`live_evaluation.db`) and 12-Instance Truncation Diagnostic (`diagnostic_evaluation.db`)

---

## 1. Phase 1 Forensic Audit Table

| # | Empirical Claim | Supporting Artifact | Verification Procedure | Audit Result | Methodological Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | *"Visual observation scaling was evaluated in the 12-instance diagnostic."* | `diagnostic_experiment/run_diagnostic_experiment.py` (lines 75–81) | Inspect image payload sent to Mistral API across conditions A–E. | **FACTUALLY REFUTED.** Every call across all 5 conditions sent the **identical full-resolution original image** (`chartqa_001.png`, etc.). Zero crops, zooms, downsampling, or visual changes occurred. | The diagnostic was purely a **prompting and decoding ceiling experiment**, not an observation-scaling experiment. Calling it "observation scaling" conflates prompt modification with sensory change. |
| **2** | *"Conditions B and C isolate the effect of generation budget."* | `diagnostic_evaluation.db` (`diagnostic_results` table) | Compare prompt, image, and settings between Condition B and Condition C. | **VERIFIED.** Image, model (`pixtral-12b-2409`), temperature ($0.0$), prompt text, and scoring were identical. Only `max_tokens` differed (60 vs. 256). | Demonstrates only that lifting the ceiling allows Pixtral-12B to finish generating answers that were cut off at 60 tokens. |
| **3** | *"Output truncation at 60 tokens caused the harmful flips in the pilot."* | `diagnostic_results` where `subset_type = 'harmful'` and `condition = 'B'` | Check `finish_reason` and `completion_tokens` on the 6 harmful instances under Condition B. | **VERIFIED.** 5 of the 6 harmful instances hit `finish_reason = 'length'` and `completion_tokens = 60`. In Condition C (`max_tokens = 256`), all 5 reached `finish_reason = 'stop'` and scored 100% correct. | Confirms root cause for this specific 6-instance subset; cannot be generalized to claim that all intervention failures across the entire benchmark were truncation. |
| **4** | *"Concise prompting (Condition D) matches expanded budget (Condition C) with $14\times$ fewer tokens."* | `diagnostic_results` for conditions D and E vs. C | Compare completion tokens and accuracy between Condition D and Condition C. | **PARTIALLY VERIFIED.** Mean completion tokens dropped from 84.7 (Cond C) to 4.1 (Cond D). Accuracy on the 12 instances was 83.3% (10/12) vs. 91.7% (11/12). | The sample size is only $N = 12$. A 1-instance difference (83.3% vs. 91.7%) has overlapping binomial intervals and cannot prove general parity. |
| **5** | *"The 12-instance diagnostic proves D-BOS is a novel and superior method."* | `intervention_diagnostic_report.md` | Audit sample selection and literature comparison. | **REJECTED.** The 12 instances were post-hoc selected based on known prior outcomes (6 known harmful, 3 known beneficial, 3 stable). No controller routing was tested. | A post-hoc diagnostic on 12 selected instances cannot serve as a benchmark or proof of a general framework. |
| **6** | *"The GVoC policy's action selection outperforms simple baselines."* | `live_evaluation.db` (100 instances) | Compare GVoC accuracy (72.0%) and C-GVoC (76.0%) against Monolithic direct inference (82.0%). | **REFUTED BY RAW PILOT DATA.** In the 100-instance live pilot, both GVoC and C-GVoC underperformed Monolithic direct inference. | The policy frequently intervened when stopping was optimal. |

---

## 2. Phase 2: Explicit Separation of Evidence Categories

To maintain research integrity, we strictly decouple five distinct claims that were previously conflated:

### Category A: Output Truncation Evidence
- **Verified Finding:** In the original pilot, the intervention prompt (*"Examine carefully with high precision..."*) caused Mistral Pixtral-12B to emit conversational preambles. Under `max_tokens = 60`, generation was severed mid-sentence before the final numerical answer was output in 8 of the 9 harmful ChartQA instances.
- **Scope:** This is an **implementation defect** of the evaluation runner, not a theoretical flaw in the underlying models.

### Category B: Answer Extraction / Prompting Evidence
- **Verified Finding:** Adding an explicit instruction (*"State only the direct, concise final answer without introductory explanation"*) suppressed conversational preambles, reducing completion length from 57.4 tokens to 4.1 tokens while avoiding truncation.
- **Scope:** This is standard prompt engineering for answer extraction. It demonstrates that format enforcement prevents preamble overhead.

### Category C: Visual Observation-Space Scaling Evidence
- **Status in Current Data:** **UNVERIFIED IN THE DIAGNOSTIC.**
- **Reason:** In both the 100-instance pilot and the 12-instance diagnostic, the model was provided with the **full original uncropped image**. Zero high-resolution cropping, multi-scale zooming, or visual transformations were tested.
- **Rule:** **We cannot claim that "observation-space scaling" succeeded when no observation change was executed.**

### Category D: GVoC Policy Action Selection Evidence
- **Status in Current Data:** **CURRENTLY UNFAVORABLE.**
- **Reason:** In the 100-instance live pilot, unregularized GVoC intervened on 100% of instances, reducing accuracy by 10 points ($p = 0.0129$) and doubling token cost. C-GVoC intervened on 48% of instances and scored 76% (vs. 82% direct).
- **Rule:** We cannot claim the controller is superior to direct inference until a controlled experiment demonstrates positive net advantage under proper implementation.

### Category E: Novelty Relative to Prior Literature
- **Status in Current Data:** **UNSUPPORTED FOR "D-BOS".**
- **Reason:** Decoupling prompt format or constraining output token length is standard practice in LLM evaluation (e.g., greedy decoding with regex/JSON schema, CoT vs. Direct Answer prompting). Calling concise prompt formatting "Dual-Budget Observation Scaling (D-BOS)" without actual sensory scaling is an overclaim that reviewers will reject.

---

## 3. Mandatory Rules for Subsequent Phases

1. **No Relabeling:** We will not label a prompt or token ceiling change as an "observation-space scaling" effect.
2. **No Post-Hoc Generalization:** The 12-instance diagnostic remains labeled strictly as a **diagnostic probe**.
3. **True Observation Transformation Required:** To test observation scaling, the experiment must execute genuine image transformations (e.g., high-resolution cropping of bounding regions vs. full downsampled views).
4. **Fair Baseline Comparison:** The controller must be compared against simple, realistic baselines (e.g., Always-Direct, Always-Intervene, and Confidence Routing) under identical generation budgets and prompt formats.
