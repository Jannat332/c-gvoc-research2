# Experiment Design and Statistical Power Analysis

**Auditors:** Empirical Methodology Auditor & ML Systems Engineer  
**Date:** October 10, 2026  
**Artifact Scope:** Confirmatory Validation of Observation Scaling, Prompt Formulation, and Generation Budgets

---

## 1. Research Objectives & Factorial Design

The objective is to rigorously isolate three distinct candidate explanations for VLM test-time performance in visual document understanding:

1. **Factor P (Prompt Formulation):** Conversational / Reasoning instructions ($P_{\text{conv}}$) vs. Concise / Format-Constrained instructions ($P_{\text{conc}}$).
2. **Factor B (Generation Budget):** Standard production ceiling ($B_{\text{low}} = 60 \text{ tokens}$) vs. Expanded reasoning ceiling ($B_{\text{high}} = 256 \text{ tokens}$).
3. **Factor O (Visual Observation State):** 
   - $O_{\text{low}}$: Downsampled/low-resolution document ($320\times 320$ pixels) where fine print is degraded below recognition thresholds.
   - $O_{\text{crop}}$: High-resolution localized optical crop ($100\%$ native sensor resolution) centered on the evidence region.
   - $O_{\text{full}}$: Full uncompressed document (reference ceiling).

### 2x2x2 Controlled Factorial Matrix

```
                      +-------------------+-------------------+
                      |   Low Budget (60) |  High Budget (256)|
+---------------------+-------------------+-------------------+
| Conv Prompt (P_conv)| Cond 1: P_c, B_l  | Cond 2: P_c, B_h  |
| Conc Prompt (P_conc)| Cond 3: P_k, B_l  | Cond 4: P_k, B_h  |
+---------------------+-------------------+-------------------+
                      ^ Evaluated across O_low and O_crop ^
```

### The Central Scientific Contrasts
1. **The Truncation Contrast:** Cond 1 vs. Cond 2 (holding $P_{\text{conv}}$ and observation constant; tests if budget alone rescues accuracy).
2. **The Prompt Bloat Contrast:** Cond 1 vs. Cond 3 (holding 60-token budget and observation constant; tests if concise guidance prevents preamble truncation).
3. **The Observation vs. Reasoning Contrast (Core Hypothesis):**
   - **Reasoning Scaling over Degraded Input:** Cond 2 on $O_{\text{low}}$ (allowing 256 tokens of CoT over blurry input).
   - **Observation Scaling:** Cond 3 on $O_{\text{crop}}$ (providing high-res crop with concise 60-token decoding).
   - **Hypothesis:** Observation scaling ($O_{\text{crop}}$) significantly outperforms reasoning scaling ($O_{\text{low}}$ + 256 tokens) when visual evidence is downsampled.

---

## 2. Statistical Power Analysis and Minimum Detectable Effect (MDE)

### A. Power Analysis for Paired Binary Outcomes (McNemar Test)
For a paired within-subject design with $N$ document instances, the statistical power to detect a difference between two conditions depends on the number of discordant pairs ($n_{10}$ and $n_{01}$):

$$\text{MDE} = \delta = p_1 - p_2$$

Given our operational budget constraint (targeting ~100 API calls to balance cost and latency on Mistral API):
- Confirmatory evaluation sample size: **$N = 20$ paired document instances** (10 DocVQA, 10 ChartQA) drawn from an untouched partition.
- Significance level: $\alpha = 0.05$ (two-sided).
- Desired power: $1 - \beta = 0.80$.

#### Power Calculation Results:
1. **Large Qualitative Effects ($\delta \ge 0.35$):**  
   If downsampling ($O_{\text{low}}$) drops baseline accuracy to $15\%$ (3/20) and high-resolution cropping ($O_{\text{crop}}$) restores accuracy to $65\%$ (13/20) ($\Delta = +50 \text{ points}$), $N = 20$ provides **statistical power $> 92\%$** ($p < 0.01$).
2. **Small Policy Refinements ($\delta \le 0.10$):**  
   If two policies differ by only 1 or 2 instances out of 20 ($\Delta = 5\text{--}10 \text{ points}$), the power is **less than $25\%$**.
3. **Explicit Limitation Declaration:**  
   **This confirmatory experiment is powered to detect large structural phenomena (e.g., whether observation scaling restores degraded visual evidence where reasoning tokens fail), but is NOT powered to detect fine-grained 2–5% policy routing margins.** We will report exact confidence intervals and will not claim equivalence for non-significant minor differences.

---

## 3. Cost and Latency Budget Estimation

- **Evaluated Instances:** $N = 20$ untouched instances.
- **Factorial Conditions Evaluated per Instance:**
  1. Baseline Direct on Full Image ($O_{\text{full}}$, $P_{\text{conc}}$, 60 tok)
  2. Degraded Direct ($O_{\text{low}}$, $P_{\text{conc}}$, 60 tok)
  3. "Think Longer" over Degraded ($O_{\text{low}}$, $P_{\text{conv}}$, 256 tok)
  4. "Look Closer" Observation Scaling ($O_{\text{crop}}$, $P_{\text{conc}}$, 60 tok)
  5. Truncation Control ($O_{\text{full}}$, $P_{\text{conv}}$, 60 tok)
- **Total Calls:** $20 \text{ instances} \times 5 \text{ conditions} = \mathbf{100 \text{ API calls}}$.
- **Estimated Token Volume:** $\approx 100 \times 750 \text{ prompt tokens} + 100 \times 40 \text{ compl tokens} \approx 79,000 \text{ tokens}$.
- **Estimated API Cost:** $\approx \$0.012$ USD (under 2 cents).
- **Estimated Runtime:** $\approx 100 \times 1.3\text{s} \approx 130\text{ seconds}$ (~2.2 minutes).
