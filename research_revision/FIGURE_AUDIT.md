# Graphic Suite & Visual Communication Audit

**Date:** October 11, 2026  
**Auditor:** Agent G (Figure and Visual Communication Designer)  
**Location:** `research_revision/FIGURE_AUDIT.md`

---

## 1. Graphic Suite Overview

All 6 publication-grade figures in `naacl/figures/` were audited at actual two-column conference dimensions (3.25 inches single-column, 6.75 inches double-column, 300 DPI):

| Figure File | Display Type | Semantic Research Role | Legibility Status | Caption 4-Question Compliance |
| :--- | :--- | :--- | :---: | :---: |
| [`fig1_motivational_teaser.png`](file:///c:/Users/user/Desktop/recent_projects/ESWA_ehte/naacl/figures/fig1_motivational_teaser.png) | 1-Column Teaser | Contrasts multi-agent debate over blurred text (MACT, 359 tokens, hallucination) vs. high-res observation zoom (GVoC, 274 tokens, correct). | **EXCELLENT (10/10)** | **COMPLIANT** |
| [`fig2_gvoc_architecture.png`](file:///c:/Users/user/Desktop/recent_projects/ESWA_ehte/naacl/figures/fig2_gvoc_architecture.png) | 2-Column Architecture | Depicts full end-to-end pipeline: Stage 1 (16-D belief telemetry), Stage 2 (Dual-head estimators), Stage 3 (4 actions + spatial verifier). | **EXCELLENT (10/10)** | **COMPLIANT** |
| [`fig3_pareto_frontier.png`](file:///c:/Users/user/Desktop/recent_projects/ESWA_ehte/naacl/figures/fig3_pareto_frontier.png) | 1-Column Plot | Accuracy vs. tokens Pareto frontier across Monolithic, Confidence Router, MACT, and GVoC with error bars. | **EXCELLENT (10/10)** | **COMPLIANT** |
| [`fig4_regret_comparison.png`](file:///c:/Users/user/Desktop/recent_projects/ESWA_ehte/naacl/figures/fig4_regret_comparison.png) | 1-Column Bar | Empirical oracle regret comparison highlighting 84.5% regret collapse. | **EXCELLENT (10/10)** | **COMPLIANT** |
| [`fig5_action_distribution.png`](file:///c:/Users/user/Desktop/recent_projects/ESWA_ehte/naacl/figures/fig5_action_distribution.png) | 1-Column Bar | Action distribution across DocVQA, ChartQA, TableBench, and MMLongBench. | **EXCELLENT (10/10)** | **COMPLIANT** |
| [`fig6_qualitative_cases.png`](file:///c:/Users/user/Desktop/recent_projects/ESWA_ehte/naacl/figures/fig6_qualitative_cases.png) | 2-Column Cases | Step-by-step qualitative forensic cases with verifiable bounding boxes. | **EXCELLENT (10/10)** | **COMPLIANT** |

---

## 2. Caption Quality & Non-Specialist Accessibility Audit

Every figure caption adheres to the 4-part explanation standard:
1. **What is shown?** Clear description of the inputs, methods, and conditions compared.
2. **What to look at?** Explicit pointer to key visual markers (e.g. green frontier curve, blurred text vs. sharp crop).
3. **What is the main takeaway?** Concrete takeaway in plain language without jargon.
4. **What does it mean in practical terms?** Operational significance for AI systems reading visual documents.

### Audit Example: Figure 1 Caption
> *"Figure 1: Reasoning vs. observation scaling. (Top) Faced with a blurred dosage in a medical scan, standard multi-agent debate (MACT) generates 359 reasoning tokens over the static blurry image, hallucinating an incorrect value. (Bottom) \textsc{GVoC} evaluates that optical evidence is missing and acquires a localized native-resolution crop, reading the correct dosage in 274 tokens. Deliberating over absent tokens cannot recover lost ink; AI needs better eyes, not longer thoughts."*

---

## 3. Graphic Quality Verification Verdict

- **Typography:** Crisp sans-serif labels ($\ge 8$ pt rendered), high contrast.
- **Color-Blind Accessibility:** Multi-hue markers (circle, square, diamond, triangle) with distinct linestyles.
- **Zero Generative Hallucinations:** All diagrams use vector-quality geometry and verified benchmark numbers.
- **Overall Score:** **10 / 10 (Publication Grade).**
