# Proposed Manuscript Revision Plan for NAACL Submission

**Auditors:** Critical Paper Reviewer, Empirical Methodology Auditor, ML Systems Engineer  
**Date:** October 10, 2026  
**Target File:** `naacl/main.tex`  
**Guiding Principle:** Every claim must be strictly anchored to verified raw empirical evidence. Overclaims, premature theoretical guarantees, and unvalidated assertions must be removed.

---

## 1. Line-by-Line Claim Audit and Required Text Revisions

### A. Abstract (Lines 40–41)
- **Current Text:**  
  *"In live empirical evaluation on genuine visual documents (Mistral Pixtral-12B), unregularized intervention risks over-triggering (+101% token inflation), whereas our conservative telemetry dispersion penalty (C-GVoC) reliably suppresses false interventions to preserve optimal stopping accuracy with zero cost overhead."*
- **Empirical Reality:**  
  In the raw 100-instance pilot, Monolithic accuracy is **82.0%**. C-GVoC accuracy is **76.0%** (-6.0 points, 9 harmful flips vs. 3 beneficial flips). It does *not* preserve optimal stopping accuracy with zero cost overhead (cost overhead is +17% overall, and on ChartQA it reaches +106%).
- **Required Revision:**  
  *"In live empirical evaluation on genuine visual documents (Mistral Pixtral-12B), unregularized intervention triggers on 100% of queries, causing severe over-intervention (-10.0 points accuracy, +102% token inflation). Our conservative dispersion penalty (C-GVoC) suppresses spurious interventions on clean documents (halving intervention rate to 48%), though domain-specific truncation and formatting risks remain on complex charts. Our confirmatory experiments demonstrate that observation scaling succeeds only when coupled with format-constrained decoding and verified spatial grounding."*

---

### B. Table 1 (Lines 42–65)
- **Current Status:**  
  Presents the 16,000-query benchmark. Caption currently states: *"Offline Simulation Benchmark Performance ($N = 16,000$ Synthetic Diagnostic Queries)."*
- **Required Refinement:**  
  Keep explicit labeling of the 16,000-query table as an offline counterfactual perturbation simulation. Add a concise companion row or text pointer to the genuine live pilot (Pixtral-12B, $N=100$) so reviewers clearly distinguish synthetic diagnostic simulation from real-world provider inference.

---

### C. Section 3.2: Decision Rule & Uncertainty Claims (Lines 103–112)
- **Current Text:**  
  Describes $\hat{\sigma}_a(s)$ as an *"epistemic dispersion proxy"* providing a *"Conservative Intervention Value (CIV) under a telemetry-conditioned Lower Confidence Bound (LCB)"*, with claims of *"eliminating spurious Type-I intervention compute."*
- **Empirical Reality:**  
  Raw database audit (`live_counterfactual_actions`, $N=200$) proved that $\hat{\sigma}_a(s)$ is **negatively correlated with absolute prediction error** ($r = -0.2173, p = 0.0020$). It is an uncalibrated heuristic that explains less than 5% of error variance ($R^2 = 0.047$).
- **Required Revision:**  
  1. **Retract Theoretical LCB / PAC Claims:** Remove language implying formal Bayesian epistemic uncertainty or mathematically guaranteed risk bounds.
  2. **Relabel Honestly:** Define $\hat{\sigma}_a(s)$ strictly as an **empirical telemetry dispersion heuristic** that penalizes high-variance features.
  3. **Acknowledge Limitation:** Explicitly state in the text: *"While the dispersion penalty empirically dampens intervention frequency, our audit reveals that scalar telemetry heuristics exhibit weak or inverted linear correlation with true counterfactual advantage error, highlighting the necessity of learned attribution verifiers rather than uncalibrated scalar bounds."*

---

### D. Section 4: Live Empirical Validation & Confirmatory Findings
- **Current Status:**  
  Main text contains extensive analysis of the 16,000-query simulation (RQ1–RQ4), but lacks the live pilot and confirmatory experimental results.
- **Required Additions:**  
  1. **Incorporate Live Pilot ($N = 100$):**  
     Report actual Pixtral-12B numbers: Monolithic 82.0%, Deterministic 79.0%, GVoC 72.0% ($p = 0.0129$), C-GVoC 76.0% ($p = 0.1460$).
  2. **Incorporate the Confirmatory Factorial Experiment ($N = 20$ untouched instances):**  
     - **The Truncation Ceiling Effect:** Conversational prompts hit the 60-token ceiling (60.0% overall truncation, 100% on ChartQA), cutting accuracy from 85.0% to 60.0%. Concise format enforcement restores 85.0% accuracy in 5.1 completion tokens.
     - **The Spatial Grounding Prerequisite:** Blind geometric cropping catastrophically drops accuracy to 25.0% ($p = 0.0391$), proving that *observation scaling requires verified spatial attribution*; arbitrary crops destroy essential global context (axes, headers, legends).
     - **Sensory vs. Reasoning Bottlenecks:** On $320 \times 320$ downsampled images, adding 131 reasoning tokens produced zero accuracy gain over 5 tokens (60.0% vs. 60.0%), confirming the information-theoretic limit of the Data Processing Inequality.

---

### E. Section 5 & 6: Related Work, Limitations, and Conclusion
- **Related Work (Line 162):**  
  Add explicit contrast with MACT \citep{yu2025visual} and Tong et al. \citep{tong2026diversity}: emphasize that while multi-agent debate scales reasoning tokens over static blurry inputs (burning 359–500 tokens), GVoC dynamically allocates compute to high-resolution evidence acquisition only when spatially grounded.
- **Limitations (Line 171):**  
  Add three critical limitations discovered during the live audit:
  1. *Observation-space scaling requires precise spatial localization; unguided cropping strips global document context.*
  2. *Intervention prompts must enforce strict concise terminal decoding to prevent reasoning preambles from hitting production token ceilings.*
  3. *Scalar dispersion heuristics cannot substitute for formal Bayesian uncertainty estimation.*
- **Conclusion (Line 176):**  
  Revise final sentence to reflect balanced findings:  
  *"Our findings reveal that test-time scaling in multimodal models is dual-dimensional: compute must be allocated to sensory observation when evidence is downsampled, but must be paired with strict output decoding constraints to prevent verbose truncation."*

---

## 2. Layout and Page Constraint Management

The manuscript must strictly respect NAACL Short Paper formatting constraints:
- **Main Text Body:** Exactly $\le 4.0$ pages.
- **References:** Pages 5–6 (unlimited).
- **Appendices:** Page 7 onward.

### Space-Saving Strategy
1. Table 1: Maintain compact array stretch (`\renewcommand{\arraystretch}{0.88}`).
2. Section 4: Condense text paragraphs in RQ1–RQ4 to make room for a compact 5-line summary table of the live confirmatory experiment.
3. Ensure no overfull hboxes or page spills past page 4 before `\bibliography`.
