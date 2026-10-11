# Shortlist Adjudication Report

**Adjudicator:** Independent Scientific Adjudicator  
**Consortium:** Literature Specialist, Math Specialist, Empirical Specialist, Skeptical Reviewer, Research Engineer  
**Date:** 2026-10-10  
**Status:** 3 Strongest Candidate Directions Selected for Decisive Empirical Evaluation.

---

## 1. Candidate Selection Summary

After auditing all 10 candidate directions against the 6 mandatory gates (Novelty, Validity, Evidence, Feasibility, Robustness, Falsification), three directions clearly emerge as scientifically viable, practically testable, and aligned with NAACL Short Paper constraints:

### Candidate 1 (Score: 92.5/100) — Risk-Bounded Counterfactual Intervention Policy (C-GVoC LCB)
- **Concept:** Subtracts an epistemic dispersion penalty ($\kappa \cdot \hat{\sigma}_a$) from estimated advantage $\hat{\Delta P}_a$, selecting actions by Lower Confidence Bound (LCB).
- **Why It Passed:** Addresses the core weakness of point-estimate GVoC (triggering expensive interventions on low-gain boundary queries). It provides a smooth, principled trade-off between conservatism and recovery.
- **Skeptical Reviewer Critique:** Is $\hat{\sigma}_a$ a real standard error or heuristic feature weighting? Must be validated with calibration coverage and sensitivity testing.

### Candidate 2 (Score: 85.5/100) — Clean-State Suppression Gating
- **Concept:** A fast deterministic pre-filter: if $d_{\text{layout}} < 0.15$ and $P_{\text{stop}} \ge 0.70$, immediately return $a_{\text{stop}}$ without evaluating candidate tool branches.
- **Why It Passed:** Eliminates Type-I intervention compute (Unnecessary Intervention Rate, UCR) on clean documents with zero FLOP overhead.
- **Skeptical Reviewer Critique:** A simple threshold rule might be seen as an ad-hoc heuristic unless integrated into the decision-theoretic framework.

### Candidate 3 (Score: 82.0/100) — Decomposed Repair-Damage Planning with Safe Abstention
- **Concept:** Decomposes net advantage into separate repair $P(Y(a)=1 \mid Y(\text{stop})=0)$ and harm $P(Y(a)=0 \mid Y(\text{stop})=1)$ probabilities, coupled with selective abstention ($a_{\text{abstain}}$) on unanswerable corruptions.
- **Why It Passed:** Directly prevents "do-no-harm" degradation on initial correct answers while safely routing unrecoverable corruptions.
- **Skeptical Reviewer Critique:** Harm events are rare in the benchmark (<2%), risking overfitting.

---

## 2. Rejection Summary of Other Candidates

- **Direction 3 (Sequential POMDP Lookahead, 69.0):** Rejected due to token inefficiency. Visual document errors are almost exclusively localized and resolved in one atomic step (e.g., zoom crop OR table re-parse). Multi-step lookahead adds token latency with negligible marginal accuracy gain.
- **Direction 6 (Distribution-Shift OOD Gating, 65.5):** Rejected due to insufficient sample size to estimate full 16-D covariance matrices reliably.
- **Direction 7 (Counterfactual Data Efficiency, 72.5):** Rejected because it changes the research problem from *test-time compute scaling* to *offline data collection*, weakening the paper's core message.
- **Direction 8 (Causal Identifiability Proofs, 72.5):** Useful as theoretical support in the Appendix, but insufficient on its own as a standalone methodological contribution.
- **Direction 10 (Conformal Prediction Intervals, 70.0):** Rejected because split conformal quantiles degenerate to zero on small calibration folds ($N=20$), making finite-sample conformal bounds overly conservative.
