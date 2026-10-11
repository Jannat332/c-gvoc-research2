# Causal Claim Audit: Disentangling Confounded Contrasts

**Auditors:** Empirical Methodology Auditor & ML Systems Engineer  
**Date:** October 10, 2026  
**Artifact Scope:** Raw results in `confirmatory_evaluation.db` across conditions C1–C5

---

## 1. The Methodological Problem: Multi-Variable Confounding

In the initial confirmatory report, contrasts were constructed that varied multiple experimental dimensions simultaneously. To uphold rigorous scientific standards, we must classify every pairwise comparison into either a **Clean Single-Factor Contrast** or a **Confounded Multi-Factor Exploratory Contrast**.

---

## 2. Taxonomy of Clean vs. Confounded Contrasts

| Contrast Pair | Variables Held Constant | Variables Varied | Scientific Classification | Valid Causal Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| **C1 vs. C5** | Image ($O_{\text{full}}$), Budget ($60 \text{ tok}$) | **Prompt Style** ($P_{\text{conc}}$ vs. $P_{\text{conv}}$) | **Clean Single-Factor Contrast** (Prompt Style) | Conversational prompting causes conversational padding that hits the 60-token ceiling (60% truncation overall, 100% on ChartQA), degrading accuracy from 85.0% to 60.0%. |
| **C1 vs. C2** | Prompt ($P_{\text{conc}}$), Budget ($60 \text{ tok}$) | **Image Resolution** ($O_{\text{full}}$ vs. $O_{\text{low}}$) | **Clean Single-Factor Contrast** (Sensory Transformation) | Downsampling from native resolution to $320\times 320$ removes fine visual ink, dropping accuracy from 85.0% to 60.0% (-25.0 points). |
| **C4 vs. C2** | Prompt ($P_{\text{conc}}$), Budget ($60 \text{ tok}$) | **Observation Framing** ($O_{\text{crop}}$ vs. $O_{\text{low}}$) | **Clean Single-Factor Contrast** (Observation Framing) | Providing an unguided center-50% crop drops accuracy from 60.0% to 25.0% ($p = 0.0391$ McNemar), proving that blind cropping destroys peripheral context (axes, legends, headers). |
| **C3 vs. C2** | Image ($O_{\text{low}}$) | **Prompt AND Budget** ($P_{\text{conv}}, 256$ vs. $P_{\text{conc}}, 60$) | **Confounded Multi-Factor Contrast** (Exploratory Only) | **Cannot attribute to budget or reasoning alone.** Changing to conversational style simultaneously with expanding budget produced identical 60.0% accuracy (12/20 vs. 12/20). |
| **C4 vs. C3** | None | **Image, Prompt, AND Budget** ($O_{\text{crop}}, P_{\text{conc}}, 60$ vs. $O_{\text{low}}, P_{\text{conv}}, 256$) | **Severely Confounded Contrast** (Invalid Causal Claim) | **Must not be cited as proof of observation scaling.** The difference (25.0% vs. 60.0%) reflects prompt, budget, and image differences simultaneously. |

---

## 3. Dissecting the Clean Single-Factor Contrasts

### A. Contrast 1: Prompt Style (C1 vs. C5 on $O_{\text{full}}$ at 60 Tokens)
- **C1 (`Full_Direct`):** Native Image + Concise Prompt + 60 tokens $\implies \mathbf{85.0\% \text{ accuracy}}$ (17/20), 0% truncation.
- **C5 (`Full_Conversational_60`):** Native Image + Conversational Prompt + 60 tokens $\implies \mathbf{60.0\% \text{ accuracy}}$ (12/20), 60% truncation (100% on ChartQA).
- **Causal Finding:** Phrasing prompts conversationally (*"Think step-by-step with high precision"*) without expanding the generation ceiling induces autoregressive verbosity that gets severed mid-sentence.
- **Limitation:** Does not prove anything about observation scaling; it is purely a decoding ceiling effect.

### B. Contrast 2: Sensory Downsampling (C1 vs. C2 on $P_{\text{conc}}$ at 60 Tokens)
- **C1 (`Full_Direct`):** Native Image + Concise Prompt + 60 tokens $\implies \mathbf{85.0\% \text{ accuracy}}$ (17/20).
- **C2 (`Degraded_Direct`):** $320\times 320$ Image + Concise Prompt + 60 tokens $\implies \mathbf{60.0\% \text{ accuracy}}$ (12/20).
- **Causal Finding:** Bilinear downsampling to $320 \times 320$ destroys high-frequency character strokes and table borders, creating a 25.0 percentage point accuracy drop under identical prompt and budget controls.

### C. Contrast 3: Observation Framing (C4 vs. C2 on $P_{\text{conc}}$ at 60 Tokens)
- **C2 (`Degraded_Direct`):** $320\times 320$ Full Image + Concise Prompt + 60 tokens $\implies \mathbf{60.0\% \text{ accuracy}}$ (12/20).
- **C4 (`Crop_Observation`):** Center 50% Crop + Concise Prompt + 60 tokens $\implies \mathbf{25.0\% \text{ accuracy}}$ (5/20).
- **Causal Finding:** When prompt and budget are strictly matched, blind center-cropping is **statistically significantly worse** than looking at the degraded full image ($p = 0.0391$ McNemar exact test).
- **Mechanism:** In ChartQA, the center crop cuts off the axis tick marks and legends at the periphery. In DocVQA, header codes, signatures, and dates outside the center 50% box are physically removed.
- **Conclusion:** **Observation-space scaling fails catastrophically if the crop is not guided by verified spatial grounding.**

---

## 4. Retraction of Confounded Claims

1. **Retraction 1:** We retract the assertion that Contrast C4 vs. C3 proved "observation scaling beats reasoning scaling." C4 and C3 varied image, prompt, and budget simultaneously.
2. **Retraction 2:** We retract any claim that C3 vs. C2 proved "reasoning tokens have zero effect." C3 altered both prompt phrasing and budget. An unconfounded test would require comparing $O_{\text{low}} + P_{\text{conc}} + 60$ against $O_{\text{low}} + P_{\text{conc}} + 256$.
3. **Core Conclusion:** The valid empirical conclusions from this confirmatory run are:
   - Sensory downsampling inflicts substantial accuracy loss (C1 vs. C2).
   - Conversational prompt instructions suffer severe truncation under 60-token ceilings (C1 vs. C5).
   - Blind geometric cropping without spatial grounding destroys document understanding (C4 vs. C2).
