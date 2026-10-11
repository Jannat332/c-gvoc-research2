# Master Research State & Tracking Ledger

**Project Title:** Think Longer or Look Closer? Test-Time Scaling for Visual Document Understanding  
**Target Venue:** NAACL (Short Paper Track: 4 pages main text + references + unlimited appendices)  
**State File Location:** `research/MASTER_STATE.md`  
**Current Date:** October 10, 2026  
**Status:** Phase 1 Complete (Integrity Gate Audited, Baseline Evidence Frozen, Style Spec Formulated). Moving to Phase 2 (Method Formalization, Related Work Consolidation, Manuscript Assembly).

---

## 1. Master State Summary

| Dimension | Current Verdict / State | Supporting Artifact |
| :--- | :--- | :--- |
| **Evidence Provenance** | Frozen databases: `live_evaluation.db` ($N=100$), `diagnostic_evaluation.db` ($N=12$), `confirmatory_evaluation.db` ($N=20$), `dataset_generator_16k.py` ($N=16,000$). | `discovery/final_integrity_gate.md` |
| **Overlap Audit** | Confirmatory 20-instance sample is **100% overlapping with pilot**; relabeled strictly as **exploratory**. | `discovery/confirmatory_overlap_audit.csv` |
| **Novelty Verdict** | Procedural multi-agent scaling (MACT, arXiv:2508.03404v2) scales reasoning over *static* visual inputs. GVoC introduces *observation-space test-time scaling* via counterfactual Value-of-Compute gating. | `research/RELATED_WORK_MATRIX.csv` |
| **Empirical Bottlenecks** | (1) Output truncation under low budgets (60 tokens) kills reasoning; concise decoding cures it. (2) Unguided cropping severs peripheral context ($p=0.0391$); spatial grounding is mandatory. | `discovery/final_integrity_gate.md` |
| **Decision Gate** | **Option A Selected**: Narrow claims to verified evidence. Present 16k benchmark as offline simulation, 100-instance live pilot as real-world diagnostic study. Retract unsupported "zero overhead" and "guaranteed regret bounds". | `research/FINAL_RESEARCH_DECISION.md` |
| **Manuscript Budget** | 4 pages main text strictly enforced. References on page 5. Appendices from page 6. | `naacl/check_pages.py` |

---

## 2. Agent Assignments and Roles

- **Agent 1 (PI / Research Strategist):** Enforce Option A; maintain claim-evidence boundary; approve all revisions.
- **Agent 2 (Literature & Novelty Auditor):** Verify primary sources (MACT, Snell 2024, Tong 2026, U-Reader, VisDocAgent, STRAND); audit `reference_audit.csv` (~35 references).
- **Agent 3 (Adversarial Reviewer):** Challenge all theoretical assertions (DPI, Proposition 1) and empirical gaps.
- **Agent 4 (Math & Algorithm Auditor):** Re-verify DPI Markov conditions ($Y^* \to X_{\text{high}} \to X_{\text{low}} \to T$) and Proposition 1 Lagrangian bounds.
- **Agent 5 (Algorithm Designer):** Produce `research/METHOD_SPEC.md` specifying state, action space, VoC objective, stopping rule, and verifier.
- **Agent 6 (Experimental Scientist):** Maintain frozen data manifests and paired statistical tests (McNemar, Wilson intervals).
- **Agent 7 (Reproducibility Engineer):** Ensure reproducible scripts for figures, tables, and latex compilation.
- **Agent 8 (Data Auditor):** Document dataset licenses, splits, and verified image hashes.
- **Agent 9 (Statistical Reviewer):** Produce `research/STATISTICAL_ANALYSIS_PLAN.md` with Bonferroni corrections and MDE bounds.
- **Agent 10 (Paper Architect & Scientific Writer):** Rewrite `naacl/main.tex` following STRAND style specification (`style_specification.md`).
- **Agent 11 (Independent Final Reviewer):** Render and audit final PDF page by page for compliance.

---

## 3. Iteration Log

- **Iteration 1 (Audit & Integrity Gate):** Identified overlap in 20-instance run; identified visual excision mechanism in 15 crop failures; audited DPI and Proposition 1. Decided on Option A.
- **Iteration 2 (Style & Structure Specification):** Extracted presentation principles from STRAND (`naacl2021_revised_v13.pdf`). Drafted `style_specification.md`.
- **Iteration 3 (In Progress):** Formulate formal method spec, related work matrix, claim ledger, and assemble submission-grade `naacl/main.tex`.
