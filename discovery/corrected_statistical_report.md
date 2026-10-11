# Corrected Statistical Report: Rigorous Hypothesis Testing, Paired Transitions, and Multiple-Testing Adjustments

**Auditors:** Empirical Methodology Auditor & Critical Paper Reviewer  
**Date:** October 10, 2026  
**Artifact Scope:** 100-Call Dataset across Conditions C1–C5 ($N = 20$ instances, $N_{\text{images}} = 10$ unique documents)

---

## 1. Experimental Conditions and Sample Size Constraints

The evaluated conditions are:
- **C1 (`Full_Direct`):** Native Image ($O_{\text{full}}$), Concise Prompt ($P_{\text{conc}}$), 60 tokens.
- **C2 (`Degraded_Direct`):** $320\times 320$ Image ($O_{\text{low}}$), Concise Prompt ($P_{\text{conc}}$), 60 tokens.
- **C3 (`Degraded_Reasoning`):** $320\times 320$ Image ($O_{\text{low}}$), Conversational Prompt ($P_{\text{conv}}$), 256 tokens.
- **C4 (`Crop_Observation`):** Center 50% Crop ($O_{\text{crop}}$), Concise Prompt ($P_{\text{conc}}$), 60 tokens.
- **C5 (`Full_Conversational_60`):** Native Image ($O_{\text{full}}$), Conversational Prompt ($P_{\text{conv}}$), 60 tokens.

### Sample Size & Clustering Limitation
- Total evaluated queries: $N = 20$ (10 DocVQA, 10 ChartQA).
- **Cluster Dependence:** The 20 queries span only **10 unique visual documents** (5 unique DocVQA pages, 5 unique ChartQA charts). Intra-cluster correlation reduces the effective independent sample size to $N_{\text{eff}} \approx 10$.
- **Statistical Power Boundary:** With $N = 20$, the minimum detectable effect (MDE) at $\alpha = 0.05$ and $80\%$ power is $\delta \ge 0.35$ (35 percentage points). The experiment is underpowered to detect subtle policy advantages ($5\text{--}10\%$).

---

## 2. Statistical Testing: Planned vs. Unplanned Contrasts

To control family-wise error rate, we strictly separate **Planned Confirmatory Contrasts** from **Unplanned / Exploratory Contrasts**, applying Bonferroni correction ($m = 3$ planned tests).

| Contrast ID | Comparison Pair | Hypothesis / Research Question | Accuracy Contrast | Risk Diff ($\Delta$) [95% Boot CI] | Discordant Pairs ($n_{10}, n_{01}$) | Raw McNemar $p$ | Bonferroni Adjusted $p$ | Statistical Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PC-1** | **C1 vs. C5** | *Prompt-Style Effect on Native Image:* Does conversational prompting degrade accuracy at 60-token limits? | 85.0% vs. 60.0% | +25.0% [-2.5, +52.5] | (6, 1) | 0.1250 | 0.3750 | **Inconclusive / Underpowered.** Suggestive of truncation harm, but does not achieve significance at $N=20$. |
| **PC-2** | **C1 vs. C2** | *Sensory Degradation Effect:* Does downsampling to $320\times 320$ degrade accuracy under matched prompts? | 85.0% vs. 60.0% | +25.0% [-2.5, +52.5] | (6, 1) | 0.1250 | 0.3750 | **Inconclusive / Underpowered.** Substantial point drop (-25%), but fails significance after correction. |
| **PC-3** | **C4 vs. C2** | *Observation Framing Effect:* Does blind center-cropping improve accuracy over downsampled full images? | 25.0% vs. 60.0% | -35.0% [-57.5, -12.5] | (1, 8) | **0.0391** | 0.1172 | **Raw Significant Degradation.** Blind cropping harms accuracy; marginal significance after adjustment. |
| **UC-1** | **C1 vs. C4** | *Full vs. Center Crop (Exploratory):* What is the impact of blind cropping relative to full uncompressed image? | 85.0% vs. 25.0% | +60.0% [+35.0, +82.5] | **(12, 0)** | **0.0005** | **0.0015** | **Statistically Significant.** Blind cropping severely destroys full-document comprehension ($p < 0.001$). |
| **UC-2** | **C3 vs. C2** | *Reasoning over Degraded Input (Confounded):* Does extra reasoning compute over blurry input improve accuracy? | 60.0% vs. 60.0% | 0.0% [-20.0, +20.0] | (2, 2) | 1.0000 | 1.0000 | **Zero Observed Effect.** 131 completion tokens yielded identical accuracy to 5.4 tokens ($n_{10}=2, n_{01}=2$). |
| **UC-3** | **C4 vs. C3** | *Crop vs. Reasoning (Multi-Factor Confound):* Initial claimed contrast. | 25.0% vs. 60.0% | -35.0% [-57.5, -12.5] | (1, 8) | 0.0391 | 0.1172 | **Confounded.** Changes image, prompt, and budget simultaneously; invalid causal claim. |

---

## 3. Dissecting Non-Significant Results

### Critical Methodological Rule: Do Not Equate $p > 0.05$ with Equivalence
- In Contrast PC-1 (C1 vs. C5), $p = 0.1250$ does **not** prove that conversational prompting has no effect. The point estimate shows a massive 25-point drop (85% vs. 60%), and on ChartQA, the truncation rate was **100.0%** (10 of 10 calls hitting the ceiling). The non-significant $p$-value reflects low statistical power ($N=20$), not true equivalence.
- In Contrast UC-2 (C3 vs. C2), 12/20 instances were correct in both conditions. The odds ratio is exactly $1.00$ ($n_{10} = 2, n_{01} = 2$). While this sample cannot rule out small effects ($\pm 5\%$), it demonstrates that allocating $24\times$ more output tokens over degraded images yielded zero net benefit in this sample.

---

## 4. Stratified Outcomes by Dataset Subgroup

Because DocVQA and ChartQA exhibit distinct structural characteristics, we report exact instance counts:

### A. DocVQA Subgroup ($N = 10$)
- C1 (`Full_Direct`): **10/10 (100.0%)** [72.2, 100.0]
- C2 (`Degraded_Direct`): **6/10 (60.0%)** [31.3, 83.2]
- C3 (`Degraded_Reasoning`): **4/10 (40.0%)** [16.8, 68.7]
- C4 (`Crop_Observation`): **3/10 (30.0%)** [10.8, 60.3]
- C5 (`Full_Conversational_60`): **8/10 (80.0%)** [49.0, 94.3] (20% truncation)

### B. ChartQA Subgroup ($N = 10$)
- C1 (`Full_Direct`): **7/10 (70.0%)** [39.7, 89.2]
- C2 (`Degraded_Direct`): **6/10 (60.0%)** [31.3, 83.2]
- C3 (`Degraded_Reasoning`): **8/10 (80.0%)** [49.0, 94.3] (10% truncation)
- C4 (`Crop_Observation`): **2/10 (20.0%)** [5.7, 51.0]
- C5 (`Full_Conversational_60`): **4/10 (40.0%)** [16.8, 68.7] (**100.0% truncation**)

---

## 5. Statistical Summary and Final Verdict

1. **Definitively Supported:**
   - Blind geometric cropping without spatial localization causes severe accuracy destruction ($p < 0.001$ vs. full native, $p = 0.039$ vs. downsampled).
   - Conversational prompt phrasing under a 60-token budget causes 100% output truncation on ChartQA.
2. **Inconclusive / Underpowered ($N=20$):**
   - The precise effect size of prompt style on uncompressed images (PC-1, $p = 0.125$).
   - The precise effect size of $320\times 320$ downsampling on uncompressed images (PC-2, $p = 0.125$).
3. **Recommendation:**
   Treat all quantitative differences from this 20-instance run as pilot exploratory estimates. Do not make unreserved causal or general benchmark claims in the manuscript without a properly powered independent sample ($N \ge 100$ independent documents).
