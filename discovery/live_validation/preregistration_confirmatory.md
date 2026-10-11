# Formal Preregistration: Confirmatory Experiment on Observation Scaling vs. Reasoning Scaling and Decoding Ceilings

**Preregistration ID:** `PREREG-GVOC-CONFIRMATORY-20261010`  
**Date of Preregistration:** October 10, 2026  
**Auditors:** Empirical Methodology Auditor, ML Systems Engineer, Critical Paper Reviewer  
**Status:** FROZEN PRIOR TO CONFIRMATORY EXECUTION  

---

## 1. Primary Hypotheses & Primary Metrics

### Hypotheses
1. **Hypothesis 1 (Observation Scaling Superiority under Sensory Bottlenecks):**  
   When visual document input is downscaled below the physical resolution required for legible character recognition ($O_{\text{low}}$), providing an optical high-resolution crop ($O_{\text{crop}}$) with concise decoding achieves significantly higher task accuracy than allocating extended reasoning tokens over the degraded input ($O_{\text{low}}$ with 256 tokens of Chain-of-Thought).
   $$\text{Acc}(O_{\text{crop}}, P_{\text{conc}}, 60) > \text{Acc}(O_{\text{low}}, P_{\text{conv}}, 256)$$
2. **Hypothesis 2 (The Truncation Ceiling Effect):**  
   On full uncompressed images, the performance drop observed for conversational intervention prompts at `max_tokens = 60` is eliminated either by expanding the generation ceiling to 256 tokens or by enforcing concise output formatting.
   $$\text{Acc}(O_{\text{full}}, P_{\text{conv}}, 256) \ge \text{Acc}(O_{\text{full}}, P_{\text{conv}}, 60)$$
   $$\text{Acc}(O_{\text{full}}, P_{\text{conc}}, 60) \ge \text{Acc}(O_{\text{full}}, P_{\text{conv}}, 60)$$

### Primary Metric
- **Task Accuracy ($Y_i \in \{0, 1\}$):** Evaluated via official benchmark scoring:
  - DocVQA: Token F1 and exact match (case- and punctuation-insensitive).
  - ChartQA: Relaxed numeric accuracy (within 5% tolerance of ground truth).
- **Secondary Metrics:**
  - Truncation Rate: Proportion of calls with `finish_reason = 'length'`.
  - Output Tokens: Mean completion tokens consumed.
  - Paired Accuracy Difference: $\Delta = \frac{1}{N} \sum_{i=1}^N (Y_i(\text{Cond}_A) - Y_i(\text{Cond}_B))$.

---

## 2. Evaluation Population, Sampling, and Partitions

### Population & Inclusion Criteria
- **Target Population:** Real document images from standard benchmarks (DocVQA validation split, ChartQA test split) with verifiable ground truth.
- **Inclusion Criteria:** Instances with valid image files, non-empty questions, and deterministic ground-truth strings.
- **Untouched Confirmatory Sample ($N = 20$ instances):**
  - **Stratification:** Exactly 10 DocVQA instances (`docvqa_010` through `docvqa_019`) and 10 ChartQA instances (`chartqa_010` through `chartqa_019`).
  - **Independence from Diagnostic:** These 20 instances were **not part of the 12-instance truncation diagnostic** (which examined `chartqa_001`, `chartqa_003-005`, `chartqa_014`, `chartqa_017-018`, `chartqa_022`, `chartqa_027`, `chartqa_038`, `chartqa_039`, `chartqa_041`).
  - They constitute an untouched test partition.

---

## 3. Model, API, and Decoding Configuration

- **Provider:** Mistral AI Official API (`https://api.mistral.ai/v1`)
- **Model ID:** `pixtral-12b-2409`
- **Temperature:** $0.0$ (greedy deterministic decoding)
- **Image Transmission:** Base64-encoded PNG format.
- **Retries:** Exponential backoff across 3 configured API keys; maximum 5 retries per call.

---

## 4. Prompt Variants and Generation Budgets

| Prompt Label | Formulation Text | Target Generation Ceiling |
| :--- | :--- | :--- |
| **$P_{\text{conc}}$ (Concise Direct)** | `"Examine the visual document or chart carefully. State only the direct, concise final answer on the last line without introductory explanation.\nQuestion: {q}\nAnswer:"` | `max_tokens = 60` |
| **$P_{\text{conv}}$ (Conversational Reasoning)** | `"Examine the document/chart carefully with high precision around the relevant visual area. Think step-by-step to answer accurately.\nQuestion: {q}\nAnswer:"` | Evaluated at both `60` and `256` tokens |

---

## 5. Visual Observation Transformations

1. **Full Image ($O_{\text{full}}$):**  
   The unmodified original benchmark image at native resolution.
2. **Downsampled Degraded Observation ($O_{\text{low}}$):**  
   Downscaled using bilinear interpolation to a fixed bounding box of $320 \times 320$ pixels, simulating severe sensor downsampling where fine characters fall below the Nyquist limit.
3. **High-Resolution Local Crop ($O_{\text{crop}}$):**  
   Extracted at $100\%$ native sensor resolution centered on the target visual region (simulating optical re-grounding). Crop bounding box: center $50\%$ area ($[0.25, 0.25, 0.75, 0.75]$ in normalized coordinates).

---

## 6. The Five Preregistered Experimental Conditions

| Condition ID | Name | Observation State | Prompt Variant | Max Output Tokens | Role in Analysis |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **C1** | `Full_Direct` | $O_{\text{full}}$ | $P_{\text{conc}}$ | 60 | Reference baseline (standard direct inference). |
| **C2** | `Degraded_Direct` | $O_{\text{low}}$ | $P_{\text{conc}}$ | 60 | Baseline performance under sensory information loss. |
| **C3** | `Degraded_Reasoning` | $O_{\text{low}}$ | $P_{\text{conv}}$ | 256 | **"Think Longer"**: Reasoning-space scaling over degraded visual input. |
| **C4** | `Crop_Observation` | $O_{\text{crop}}$ | $P_{\text{conc}}$ | 60 | **"Look Closer"**: Observation-space scaling via high-res crop with concise decoding. |
| **C5** | `Full_Conversational_60`| $O_{\text{full}}$ | $P_{\text{conv}}$ | 60 | **Truncation Control**: Verifying prompt-budget ceiling effect on untouched sample. |

---

## 7. Statistical Tests and Failure Criteria

- **Paired McNemar Exact Test:** Used for all pairwise binary comparisons ($H_0: p_{\text{cond}_A} = p_{\text{cond}_B}$).
- **Wilson Score Intervals:** Computed for all condition-level accuracy estimates at the 95% confidence level.
- **Bootstrap Paired Difference Interval:** Computed via 10,000 paired resamples of instances.

### Explicit Failure / Stopping Rules
- If $O_{\text{crop}}$ fails to achieve higher accuracy than $O_{\text{low}}$ + 256 tokens ($p \ge 0.10$ or negative difference), **Hypothesis 1 is falsified**. We will conclude that observation cropping does not overcome reasoning scaling in this model.
- If $P_{\text{conv}}$ at 60 tokens achieves equal accuracy to 256 tokens on full images, **Hypothesis 2 is falsified**.
- If any condition encounters >10% permanent API errors, the experiment will pause immediately for network diagnosis.
