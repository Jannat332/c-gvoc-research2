# Figure Audit — Loop 1 (Comprehensive Q1 Journal Review Panel)

**Target Venue**: *Elsevier Expert Systems with Applications* (ESWA, Impact Factor: 8.5, CiteScore: 14.2, Top 3% Q1)  
**Manuscript Title**: *Grounded Value-of-Compute: Cost-Aware Process Intervention for Reliable Visual Document Understanding*  
**Date of Audit**: September 18, 2026  
**Audit Scope**: Full Graphic Suite (Figures 1 through 6)

---

## Panel Composition & Reviewer Profiles

To ensure a rigorous, multi-faceted evaluation, three distinct specialist reviewers conducted independent evaluations:

1. **Reviewer 1 (Systems & Process Methodology Specialist)**: Evaluates structural fidelity, perception-decision workflow logic, POMDP mathematical consistency, and semantic clarity between baseline debates and surgical interventions.
2. **Reviewer 2 (Empirical Data, Statistics & Visualization Specialist)**: Evaluates empirical completeness, coordinate accuracy, benchmark baseline representation ($N=16,000$), axis scaling, error bounds, and Pareto dominance rigor.
3. **Reviewer 3 (Elsevier Production Editor & Publication Cartographer)**: Evaluates typographical cohesion, font sizing at 100% journal column width, vector/raster artifacting, color-blind accessibility, and compliance with the *Elsevier Guide for Authors*.

---

## 1. Reviewer 1: Systems & Process Methodology Report

### Individual Figure Assessment

* **Figure 1 (Motivational Teaser)**:
  * *Strengths*: Effective visual contrast between ungrounded multi-agent debate (MACT) and surgical perception repair (GVoC). Clear visual flow from document downsampling to terminal outcome.
  * *Critique*: The mathematical ratio $V(s,a) = \frac{\Delta P}{Cost} > 0$ in Panel B should explicitly include the cost regularization parameter $\epsilon$ ($V(s,a) = \frac{\Delta P}{Cost + \epsilon} > 0$) to align with Section 3.3.
  * *Score*: **8.5 / 10**

* **Figure 2 (System Architecture)**:
  * *Strengths*: Outstanding horizontal three-stage layout with modern card aesthetics.
  * *Critique (FATAL)*: The green estimator trapezoid in Stage 2 contains generative AI pseudo-math ($\Delta I \lor V - \Delta P$) and nonsense label *"UA estimation heads"*. Furthermore, the crop in Stage 3 contains hallucinated gibberish text (*"n and Poopeter Cons..."*). In a top-tier Elsevier journal, this will trigger immediate rejection for AI-generated visual hallucination. The dual heads must explicitly represent the Advantage Head $\hat{\Delta P}$ and Marginal Cost Head $\hat{C}$.
  * *Score*: **6.0 / 10**

* **Figure 3 (Pareto Frontier)**:
  * *Strengths*: Highly engaging infographic layout; clearly denotes the "Compute Bloat Regime".
  * *Critique*: Only plots 3 points (Monolithic, GVoC, MACT). The paper evaluates 7 configurations in Table 1 (including Always Re-Ground, Always Re-Exec, Deterministic Rules, and Action Oracle). Omitting the other 4 methods weakens the methodological justification for selective Value-of-Compute gating.
  * *Score*: **7.5 / 10**

* **Figure 4 (Oracle Decision Regret)**:
  * *Strengths*: Outstanding bar chart layout. Perfectly conveys the 84.5% regret collapse.
  * *Critique*: Minor. Add explicit indication of sample size ($N=16,000$) and denote that regret represents expected loss divergence $\mathcal{R}$.
  * *Score*: **9.0 / 10**

* **Figure 5 (Action Distribution)**:
  * *Strengths*: Demonstrates modality-adaptive behavior (DocVQA optical crop vs. TableBench schema realignment).
  * *Critique*: Abstention ($a_{\text{abstain}}$) is 0.0% across all benign benchmarks. Add a brief annotation clarifying that $a_{\text{abstain}}$ is triggered under synthetic corruption stress testing (Appendix G) while benign documents exhibit positive salvage value.
  * *Score*: **8.5 / 10**

* **Figure 6 (Qualitative Cases)**:
  * *Strengths*: Superb dual-panel layout with dedicated badges and structured numbered steps.
  * *Critique*: Enhancing the visual crop elements with real bounding box coordinates $[y_{\min}, x_{\min}, y_{\max}, x_{\max}]$ will ground the case study in the paper's spatial taxonomy.
  * *Score*: **8.5 / 10**

**Reviewer 1 Overall Score**: **8.00 / 10**

---

## 2. Reviewer 2: Empirical Data, Statistics & Visualization Report

### Individual Figure Assessment

* **Figure 1 (Motivational Teaser)**:
  * *Critique*: The token expenditure numbers (359 vs 274) and accuracy (64.4% vs 70.2%) match Table 1, but the regret values (2.659 vs 0.412) should specify the sample population ($N=16,000$).
  * *Score*: **8.5 / 10**

* **Figure 2 (System Architecture)**:
  * *Critique*: Stage 1 lists only 3 features (Visual Uncertainty, Spatial Density, Cross-modal Alignment), missing the 4th fundamental feature dimension: Historical Token Cost $C_{\text{prior}}$. The mathematical parameter $\tau$ is written as English word *"threshold"*.
  * *Score*: **6.5 / 10**

* **Figure 3 (Pareto Frontier)**:
  * *Critique (MAJOR)*: To prove Pareto dominance under empirical peer review, the figure must plot all evaluated benchmark baselines:
    1. Monolithic Zero-Shot (250 tok, 12.5%)
    2. GVoC Proposed (274 tok, 70.2%)
    3. MACT Baseline (359 tok, 64.4%)
    4. Always Re-Ground (392 tok, 58.6%)
    5. Always Re-Exec (446 tok, 52.4%)
    6. Deterministic Rule Baseline (368 tok, 89.0%)
    7. Action Oracle Upper Bound (344 tok, 90.3%)
    The current concept rendering only displays 3 points, which constitutes an incomplete empirical presentation.
  * *Score*: **7.0 / 10**

* **Figure 4 (Oracle Decision Regret)**:
  * *Critique*: Excellent data visualization. Adding the exact paired difference significance ($p < 0.001$, McNemar test) in the annotation will make it bulletproof.
  * *Score*: **9.2 / 10**

* **Figure 5 (Action Distribution)**:
  * *Critique*: Numerical data perfectly matches Table 10. Grouped bar geometry is clean and legible.
  * *Score*: **9.0 / 10**

* **Figure 6 (Qualitative Cases)**:
  * *Critique*: The arithmetic delta in Case 2 ($+\$22.4\text{M} = \$34.8\text{M} - \$12.4\text{M}$) and the co-payment in Case 1 ($\$185.50$) are 100% faithful to the qualitative logs.
  * *Score*: **8.8 / 10**

**Reviewer 2 Overall Score**: **8.17 / 10**

---

## 3. Reviewer 3: Elsevier Production Editor & Publication Cartographer Report

### Individual Figure Assessment

* **Figure 1 (Motivational Teaser)**:
  * *Critique*: Card design is modern and aesthetic. Verify that font rendering at single/double column print dimensions is crisp and exceeds 300 DPI.
  * *Score*: **8.8 / 10**

* **Figure 2 (System Architecture)**:
  * *Critique (REJECT AS-IS)*: Header text has inconsistent case: *"framework for visual Document Understanding"*. The synthetic text inside the crop box is visibly blurred and unreadable. Must be replaced with crisp vector/raster typography adhering to Elsevier typesetting rules.
  * *Score*: **6.0 / 10**

* **Figure 3 (Pareto Frontier)**:
  * *Critique*: Axis lines, tick marks, and labels are well-styled, but the green star icon has slight anti-aliasing artifacts. A vector-crisp Pareto chart adhering to the same palette is required.
  * *Score*: **8.0 / 10**

* **Figure 4 (Oracle Decision Regret)**:
  * *Critique*: Outstanding typography and bar hierarchy. Spines and gridlines conform to standard Elsevier scientific chart requirements.
  * *Score*: **9.2 / 10**

* **Figure 5 (Action Distribution)**:
  * *Critique*: Excellent contrast and readability. Colors are distinguishable for readers with common color vision deficiencies.
  * *Score*: **9.0 / 10**

* **Figure 6 (Qualitative Cases)**:
  * *Critique*: Excellent balance between Panels A and B. Container elevation shadows and border radii are consistent with Figures 1 and 2.
  * *Score*: **8.8 / 10**

**Reviewer 3 Overall Score**: **8.30 / 10**

---

## Loop 1 Summary Scorecard

| Figure # | Reviewer 1 (Systems) | Reviewer 2 (Empirical) | Reviewer 3 (Production) | Mean Score | Status |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Figure 1** | 8.5 | 8.5 | 8.8 | **8.60 / 10** | Minor Polish |
| **Figure 2** | 6.0 | 6.5 | 6.0 | **6.17 / 10** | **Critical Revision Required** |
| **Figure 3** | 7.5 | 7.0 | 8.0 | **7.50 / 10** | **Major Revision Required** |
| **Figure 4** | 9.0 | 9.2 | 9.2 | **9.13 / 10** | Approved / Polish |
| **Figure 5** | 8.5 | 9.0 | 9.0 | **8.83 / 10** | Approved / Polish |
| **Figure 6** | 8.5 | 8.8 | 8.8 | **8.70 / 10** | Approved / Polish |
| **Overall Panel** | **8.00** | **8.17** | **8.30** | **8.16 / 10** | **REVISE TO REACH 10.0** |

---

## Mandatory Remediation Action Plan for Loop 2

1. **Figure 2 Overhaul (Target: 10/10)**:
   - Surgically eliminate the AI pseudo-math trapezoid in Stage 2.
   - Insert formal **Dual Estimator Heads**: Head 1 (Advantage $\hat{\Delta P}_a$) and Head 2 (Marginal Cost $\hat{C}_a$) with exact ratio $V(s_t,a) = \frac{\hat{\Delta P}_a}{\hat{C}_a + \epsilon} > \tau$.
   - Replace the synthetic gibberish text in Stage 3 with an ultra-crisp 300 DPI optical table crop matching Figure 1 (`Line 14b: $185.50` or invoice total).
   - Fix header title to formal title case: *"Figure 2: Grounded Value-of-Compute (GVoC) Architecture: 3-Stage Perception-Decision Pipeline"*.
   - Add the 4th telemetry dimension ($C_{\text{prior}}$).

2. **Figure 3 Empirical Completion (Target: 10/10)**:
   - Re-generate Figure 3 in the exact card-and-badge modern aesthetic that the user loved, while **plotting all 7 evaluated benchmarks**: Monolithic (12.5%), GVoC (70.2%), MACT (64.4%), Always Re-Ground (58.6%), Always Re-Exec (52.4%), Deterministic Rules (89.0%), and Action Oracle (90.3%).
   - Include the shaded "Compute Bloat Regime" and the Pareto dominance vector from MACT to GVoC (+5.8% Acc, -23.7% Tokens).

3. **Figure 1 Polish (Target: 10/10)**:
   - Ensure cost regularization $\epsilon$ is noted in the decision ratio ($V(s,a) = \frac{\Delta P}{Cost + \epsilon} > 0$).
   - Ensure typography is 100% crisp.

4. **Figure 4 & 5 Polish (Target: 10/10)**:
   - Figure 4: Add explicit $p < 0.001$ statistical significance annotation.
   - Figure 5: Add footnote callout for $a_{\text{abstain}}$ activation during stress testing.

5. **Figure 6 Polish (Target: 10/10)**:
   - Add explicit normalized bounding box coordinates $[0.724, 0.451, 0.779, 0.578]$ to the visual evidence thumbnails.

6. **File Organization Constraint**:
   - Save only the primary high-resolution `.png` (and `.pdf` for LaTeX) in `paper_final/figures/`.
   - Move all generator scripts and scratch files into `archive/`.
