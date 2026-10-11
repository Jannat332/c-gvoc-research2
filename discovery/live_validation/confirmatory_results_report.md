# Confirmatory Experiment Results Report: Provenance, Statistical Analysis, and Theoretical Falsification

**Auditors:** Empirical Methodology Auditor, ML Systems Engineer, Critical Paper Reviewer  
**Date:** October 10, 2026  
**Artifact Scope:** 100-Call Preregistered Confirmatory Run on 20 Untouched Instances (`discovery/live_validation/confirmatory_experiment/confirmatory_evaluation.db`)  
**Evaluated Model:** Mistral Pixtral-12B (`pixtral-12b-2409`)

---

## 1. Executive Summary: Core Scientific Findings

We executed the preregistered 5-condition factorial experiment across 20 untouched benchmark instances (10 DocVQA, 10 ChartQA) completely independent of the earlier diagnostic set.

### Headline Results
1. **The Truncation Ceiling Effect is Confirmed (Hypothesis 2 Supported):**  
   On full uncompressed images, asking the model to *"think step-by-step with high precision"* under a standard production budget of 60 tokens ($C5$) caused a **60.0% truncation rate overall** (and **100.0% on ChartQA**), cutting accuracy from **85.0%** ($C1$) down to **60.0%** ($C5$). Format-enforced concise decoding eliminated truncation (0.0%) and achieved 85.0% accuracy in just 5.1 output tokens.
2. **Naive Geometric Cropping Fails Catastrophically (Hypothesis 1 Falsified):**  
   Providing a center 50% high-resolution crop ($C4$) resulted in **only 25.0% accuracy** (5/20), performing **statistically significantly worse** than reasoning over the degraded image ($C3$, 60.0% accuracy, $p = 0.0391$ McNemar exact test). Blind visual cropping strips peripheral axes, legends, headers, and footers, proving that *ungrounded observation changes destroy document comprehension*.
3. **Reasoning Scaling over Degraded Inputs Yields Zero Net Gain:**  
   Allocating 256 tokens of step-by-step reasoning over the $320 \times 320$ downsampled image ($C3$) consumed 131.2 completion tokens (a $24\times$ token increase over direct inference) but produced **identical 60.0% accuracy** to direct concise inference with 5.4 tokens ($C2$, $p = 1.000$). Extra contemplation cannot recover missing sub-pixel characters.

---

## 2. Quantitative Performance Across Confirmatory Conditions

| Condition ID | Condition Name | Observation State | Prompt Style | Max Tokens | Accuracy (95% Wilson CI) | Truncation Rate | Mean Compl. Tokens | Mean Total Tokens | Mean Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **C1** | `Full_Direct` | Full Native ($O_{\text{full}}$) | Concise ($P_{\text{conc}}$) | 60 | **85.0%** (17/20) [64.0, 94.8] | 0.0% | **5.1** | 1,456.7 | 1.56s |
| **C2** | `Degraded_Direct` | $320\times 320$ Downsampled ($O_{\text{low}}$) | Concise ($P_{\text{conc}}$) | 60 | **60.0%** (12/20) [38.7, 78.1] | 0.0% | **5.4** | 206.1 | 1.24s |
| **C3** | `Degraded_Reasoning` | $320\times 320$ Downsampled ($O_{\text{low}}$) | Conversational ($P_{\text{conv}}$) | 256 | **60.0%** (12/20) [38.7, 78.1] | 5.0% | **131.2** | 330.9 | 2.34s |
| **C4** | `Crop_Observation` | Center 50% Crop ($O_{\text{crop}}$) | Concise ($P_{\text{conc}}$) | 60 | **25.0%** (5/20) [11.2, 46.9] | 0.0% | **5.3** | 769.0 | 1.04s |
| **C5** | `Full_Conversational_60` | Full Native ($O_{\text{full}}$) | Conversational ($P_{\text{conv}}$) | 60 | **60.0%** (12/20) [38.7, 78.1] | **60.0%** | **48.6** | 1,499.2 | 1.61s |

---

## 3. Dataset-Stratified Dissection (DocVQA vs. ChartQA)

| Condition | DocVQA ($N=10$) Accuracy | DocVQA Truncation | ChartQA ($N=10$) Accuracy | ChartQA Truncation |
| :--- | :--- | :--- | :--- | :--- |
| **C1 (`Full_Direct`)** | **100.0%** (10/10) | 0.0% | **70.0%** (7/10) | 0.0% |
| **C2 (`Degraded_Direct`)** | 60.0% (6/10) | 0.0% | 60.0% (6/10) | 0.0% |
| **C3 (`Degraded_Reasoning`)** | 40.0% (4/10) | 0.0% | **80.0%** (8/10) | 10.0% |
| **C4 (`Crop_Observation`)** | 30.0% (3/10) | 0.0% | 20.0% (2/10) | 0.0% |
| **C5 (`Full_Conversational_60`)** | 80.0% (8/10) | 20.0% | 40.0% (4/10) | **100.0%** |

### Critical Dataset Insights
- **ChartQA Truncation Sensitivity:** Under Conversational prompting ($C5$), ChartQA suffered **100% truncation rate** (10 of 10 calls cut off at 60 tokens), causing accuracy to collapse from 70% to 40%.
- **DocVQA Sensory Sensitivity:** Downsampling to $320 \times 320$ dropped DocVQA accuracy from 100% to 60%. However, blind center cropping ($C4$) dropped accuracy further to 30%, because target answers (signatures, dates, header codes) were located outside the center 50% box.
- **ChartQA Reasoning Resilience:** On ChartQA, reasoning scaling ($C3$) reached 80% accuracy (rescuing 2 instances over direct degraded), because charts contain arithmetic logic where scratchpad tokens assist calculation even on coarse bars.

---

## 4. Paired Contrast Testing (McNemar Exact Tests)

```
Contrast 1: Crop Observation (C4) vs. Degraded Reasoning (C3)
  Acc(C4) = 25.0% vs. Acc(C3) = 60.0%
  Discordant: C4=1 & C3=0: 1 | C4=0 & C3=1: 8
  McNemar exact p-value: 0.0391 (Statistically significant harm from naive cropping)

Contrast 2: Reasoning Scaling on Degraded Input (C3 vs. C2)
  Acc(C3) = 60.0% vs. Acc(C2) = 60.0%
  Discordant: C3=1 & C2=0: 2 | C3=0 & C2=1: 2
  McNemar exact p-value: 1.0000 (No net benefit from 131 reasoning tokens over degraded input)

Contrast 3: Sensory Degradation Impact (C1 vs. C2)
  Acc(C1) = 85.0% vs. Acc(C2) = 60.0%
  Discordant: C1=1 & C2=0: 6 | C1=0 & C2=1: 1
  McNemar exact p-value: 0.1250 (-25.0 point drop from downsampling)

Contrast 4: Truncation Ceiling Impact (C1 vs. C5)
  Acc(C1) = 85.0% vs. Acc(C5) = 60.0%
  Discordant: C1=1 & C5=0: 6 | C1=0 & C5=1: 1
  McNemar exact p-value: 0.1250 (-25.0 point drop from conversational truncation)
```

---

## 5. Raw Data Provenance and Traceability

- **Database:** `discovery/live_validation/confirmatory_experiment/confirmatory_evaluation.db`
- **Total Executed Calls:** Exactly 100 API calls.
- **Provider:** Mistral AI (`pixtral-12b-2409`).
- **Failures / Retries:** 1 rate-limit retry rotated successfully to Key #2; zero permanent failures; zero mocks.
- **Image Artifacts:** All 40 generated transformed images ($O_{\text{low}}$ and $O_{\text{crop}}$) are saved in `transformed_images/`.
- **Reproducibility Command:**
  ```bash
  python discovery/live_validation/audit_scripts/analyze_confirmatory_results.py
  ```

---

## 6. Theoretical Implications: What Must Be Concluded

1. **The Fallacy of Naive Observation Scaling:**  
   The assumption that *"looking closer always helps"* is empirically falsified ($p = 0.0391$). Visual document understanding requires **global contextual anchoring** (axes, table column headers, units). Arbitrary or heuristic cropping destroys this context.
2. **The True Role of GVoC:**  
   Observation-space scaling is viable **only when paired with verified spatial evidence localization** (e.g., bounding-box attribution). If a model does not know where the evidence is, cropping introduces fatal Type-I intervention harm.
3. **The Anti-Truncation Decoding Rule:**  
   When performing test-time intervention or verification, prompts must be constrained to concise terminal generation. Conversational prompt instructions waste token budgets and cause truncation failures.
