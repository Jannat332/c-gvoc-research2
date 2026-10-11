# NAACL Submission Readiness Checklist

**Document:** `research/SUBMISSION_CHECKLIST.md`  
**Date:** October 10, 2026  
**Venue:** NAACL (Short Paper Track: 4 pages main text + references + unlimited appendices)

---

## 1. Supervisor-Alignment & Master Gate Status

- [x] **Coherent Storyline:** Progression from real-world medical/invoice reading dilemma to specific downsampling failure, research gap, method, experiments, and limitations audited and verified (`research/transition_audit.md`).
- [x] **Motivating Example:** Figure 1 (Motivational Teaser) and Table 1 present a concrete before-and-after document query demonstrating reasoning hallucinations vs. observation zoom.
- [x] **Architecture Figure:** Figure 2 illustrates the complete end-to-end GVoC pipeline with belief state telemetry, dual-head estimators, 4-action space, and spatial verifier.
- [x] **Results Figure:** Figure 3 plots the empirical Pareto frontier across all benchmark methods with error bars and significance notations.
- [x] **Legible Figures & Captions:** All figure captions answer the 4 questions (What is shown? What to look at? What is the main takeaway? What does it mean?) in non-specialist accessible prose.
- [x] **Verified References:** Exactly 35 genuine references compiled in `research/reference_audit.csv` with zero hallucinated entries.
- [x] **Page Budget Compliance:** Main text occupies strictly 4 pages. References begin on page 5. Appendices begin on page 7.
- [x] **Evidence Separation:** 16,000-query benchmark is explicitly framed as an offline simulation; 100-instance pilot is framed as a live deployment case study; 20-instance run is labeled exploratory.
- [x] **Mathematical Integrity:** Data Processing Inequality states explicit Markov chain assumptions ($Y^* \to X_{\text{high}} \to X_{\text{low}} \to T$) and is framed as an upper bound on reasoning, not an algorithmic proof of cropping. Proposition 1 is qualified as stylized sensitivity analysis.
- [x] **Causal Language Clean:** All unreserved causal claims ("decisively outperforms", "proves", "eliminates Type-I errors") replaced with descriptive statistical findings.
- [x] **Zero Overclaiming:** Retracted unsupported claims of "zero cost overhead" and "guaranteed regret bounds".
- [x] **Reproducibility Commands:** All reproduction commands documented and verified (`research/REPRODUCIBILITY.md`).

---

## 2. Final Submission Readiness Verdict

**Verdict:** **SUBMISSION-READY UNDER NARROWED, EMPIRICALLY DEFENDED CLAIMS (OPTION A)**  
The paper is scientifically sound, methodologically transparent, adheres strictly to NAACL length constraints, and provides a compelling, well-supported conceptual and empirical contribution to the multimodal test-time scaling literature.
