# Research Path Selection & Final Contribution Decision

**Date:** October 11, 2026  
**Auditors:** Agent A (Principal Investigator) & Agent C (Adversarial Reviewer)  
**Location:** `research_revision/CONTRIBUTION_DECISION.md`

---

## 1. Evaluation of Candidate Research Paths

| Strategic Path | Description & Framing | Evidence Support in Repo | Fatal Risks / Blockers | Verdict |
| :--- | :--- | :--- | :--- | :---: |
| **Path A: Method Superiority Paper** | Claim that GVoC is a superior controller that beats monolithic models and MACT across all settings with zero overhead. | Supported in 16k simulation (+5.8% over MACT). | **FATAL BLOCKER:** Live pilot on Mistral Pixtral-12B showed accuracy degradation (-10% for GVoC, -6% for C-GVoC) and +17% to +101% token inflation. Claiming live superiority is factually false. | **REJECTED** |
| **Path B: Empirical Diagnostic Paper** | Position the work as an empirical study investigating when observation scaling helps vs. hurts, highlighting failure modes. | Fully supported by both live pilot ($N=100$), diagnostic probe ($N=12$), and factorial probe ($N=20$). | Risk of losing the formal decision-theoretic framework that connects test-time compute to Value of Computation. | **PARTIALLY ADOPTED** |
| **Path C: Benchmark & Evaluation Paper** | Benchmark accuracy, cost, and visual transformations across document datasets without a unified algorithm. | Supported across the 4 evaluated datasets. | Lacks a distinctive methodological contribution for NAACL. | **REJECTED** |
| **Path A/B Hybrid (RECOMMENDED)** | **Decision-Theoretic Framework + Empirical Bottleneck Diagnostic:** Formalize GVoC as an observation-space decision framework; validate its potential in offline simulation; diagnose the Truncation Trap and Grounding Prerequisite on live models. | **100% Traceable to Evidence:** Simulation results are labeled as simulation; live pilot results are reported with complete honesty (including negative gaps). | Zero false claims. Directly addresses skeptical reviewer concerns while delivering a genuine, defensible contribution. | **SELECTED** |

---

## 2. Final Contribution Statement

The paper makes three specific, evidence-backed contributions:

1. **A Formal Decision-Theoretic Framework for Observation-Space Scaling:**
   We formalize test-time compute allocation between observation space and reasoning space under the Grounded Value-of-Compute (GVoC) ratio $\mathcal{V}(s, a) = (\hat{\Delta P}_a - \lambda \hat{\sigma}_a) / (C_a + \epsilon)$. In an offline 16,000-query benchmark simulation across four document datasets, GVoC reaches 70.2% accuracy—improving over multi-agent debate (MACT) by +5.8 points while using 23.7% fewer tokens.
2. **Empirical Discovery of the Truncation Ceiling Trap (Engineering Finding):**
   Through targeted live diagnostic probes on Mistral Pixtral-12B, we reveal that conversational instructions cause catastrophic completion truncation (up to 100% on ChartQA) under standard production budgets (60 tokens), cutting accuracy. Format-constrained concise decoding completely eliminates truncation (0.0%) and restores accuracy in minimal tokens.
3. **Empirical Discovery of the Grounding Prerequisite (Perceptual Finding):**
   Through controlled live factorial comparisons, we demonstrate that unguided geometric cropping causes severe performance degradation (falling from 60.0% to 25.0%, $p = 0.0391$) by physically excising peripheral context (headers, axes, legends, page numbers). This establishes that spatial grounding is a mandatory prerequisite for observation scaling.
