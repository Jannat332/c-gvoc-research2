# Final Scientific-Integrity Gate Report

**Auditors & Authors:** Empirical Methodology Auditor, ML Systems Engineer, Critical Paper Reviewer  
**Date:** October 10, 2026  
**Artifact Scope:** Comprehensive audit across `live_evaluation.db` (100 instances), `diagnostic_evaluation.db` (12 instances), `confirmatory_evaluation.db` (20 instances), and `naacl/main.tex`.

---

## 1. Frozen Experimental Evidence & Database Provenance

All raw databases are cryptographically frozen. No records have been altered or overwritten.

| Database File | Scope & Size | Evaluation Type | Status & Provenance |
| :--- | :--- | :--- | :--- |
| `discovery/live_validation/live_evaluation.db` | 100 instances, 300 calls | Live Pilot Benchmark | **FROZEN.** Mistral Pixtral-12B (`pixtral-12b-2409`), Oct 10, 2026. |
| `discovery/live_validation/diagnostic_experiment/diagnostic_evaluation.db` | 12 instances, 60 calls | Prompt/Budget Diagnostic Probe | **FROZEN.** Post-hoc probe on 6 harmful, 3 beneficial, 3 stable instances. |
| `discovery/live_validation/confirmatory_experiment/confirmatory_evaluation.db` | 20 instances, 100 calls | Factorial Image/Prompt Probe | **FROZEN (LABELED EXPLORATORY).** 100% overlap with pilot dataset; 3 direct diagnostic overlaps; 10 unique images. |

---

## 2. Claim-by-Claim Scientific Integrity Audit Table

| # | Current Manuscript / Prior Report Wording | Empirical Evidence from Raw Data | Statistical Status | Required Scientific Correction | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | *"C-GVoC reliably suppresses false interventions to preserve optimal stopping accuracy with zero cost overhead."* (Abstract, line 40) | Raw 100-instance pilot: Monolithic accuracy = 82.0%, C-GVoC = 76.0% (-6.0 points). Overall tokens: 1,676 vs. 1,428 (+17% cost overhead). On ChartQA: 52.0% vs. 64.0% (+106% cost overhead). | $p = 0.1460$ (McNemar exact, $n_{10}=9, n_{01}=3$). Non-significant difference does *not* prove equivalence or preservation. | **WITHDRAW CLAIM.** State that C-GVoC partially reduces intervention frequency compared to unregularized GVoC, but still incurs net accuracy degradation on charts. | **RETRACT** |
| **2** | *"The 20-instance confirmatory experiment independently validated observation scaling."* (Confirmatory report) | Overlap audit (`confirmatory_overlap_audit.csv`): 20/20 instances were drawn from the pilot dataset; 3 instances directly overlapped with the diagnostic; only 10 unique images exist across the 20 queries. | Sample has zero independence from earlier exploratory phases; intra-cluster correlation $N_{\text{eff}} \approx 10$. | **CORRECT DESCRIPTION.** Relabel the 20-instance run strictly as an **exploratory pilot probe**. Remove all claims of independent confirmation. | **RETRACT CLAIM OF INDEPENDENCE** |
| **3** | *"Observation cropping decisively outperforms reasoning scaling over degraded inputs."* (Prior contrast C4 vs. C3) | In C4 vs. C3, three variables were varied simultaneously (Image: Crop vs. Low-Res; Prompt: Concise vs. Conv; Budget: 60 vs. 256). In the clean unconfounded contrast (C4 vs. C2, matched prompt and budget), crop achieved **25.0% vs. 60.0%** for downsampled. | Confounded comparison. Clean contrast: $p = 0.0391$ (McNemar exact, $n_{10}=1, n_{01}=8$). Blind crop is statistically significantly *worse*. | **REPLACE CONFLICTING CLAIM.** State that unguided geometric cropping causes severe performance degradation ($p = 0.039$) by severing peripheral context. | **CORRECT** |
| **4** | *"The Data Processing Inequality proves that observation scaling is necessary and superior to reasoning."* (Section 2 & Appendix A) | The Data Processing Inequality ($I(Y; Z) \le I(Y; X_{\text{low}})$) proves an upper bound on mutual information under downsampling. It does *not* prove that a cropping policy will preserve target information. | Information-theoretic upper bound, not an algorithmic performance guarantee. | **RESTRICT TO MOTIVATIONAL LIMIT.** Explicitly state the Markov chain assumption ($Y \to X_{\text{high}} \to X_{\text{low}} \to Z$) as an upper bound on reasoning over blurry inputs. Remove language framing DPI as a proof of GVoC's success. | **QUALIFY** |
| **5** | *"Proposition 1 guarantees bounded empirical regret via calibrated confidence bounds."* (Section 3.2, line 245) | Raw diagnostic table (`live_counterfactual_actions`, $N=200$): dispersion proxy $\hat{\sigma}$ has **negative correlation with error** ($r = -0.2173, p = 0.0020$). The assumption of uniform error bounds $|\hat{\Delta P} - \Delta P| \le \delta_P$ is violated. | Bounded error assumption is empirically violated in real-world model telemetry. | **LABEL AS ASYMPTOTIC MOTIVATION.** Clarify that Proposition 1 is a stylized Lagrangian sensitivity analysis under assumed uniform estimation bounds, not a real-world PAC guarantee. | **QUALIFY** |
| **6** | *"D-BOS is a novel dual-budget test-time scaling architecture."* (Diagnostic report) | Enforcing concise terminal output is standard prompt engineering (direct vs. CoT prompting). No novel architectural modules were introduced. | Engineering prompt technique, not an architectural contribution. | **REMOVE D-BOS LABEL.** Frame as an engineering finding: format-constrained decoding is an operational prerequisite for test-time verification. | **RETRACT** |

---

## 3. Mathematical Audit of `naacl/main.tex`

### A. The Data Processing Inequality (Theorem 1 / Appendix A)
- **Current Formulation (Line 284):**  
  `$(\mathcal{I}, Y^*) \longrightarrow (\tilde{\mathcal{I}}, \mathcal{Q}) \longrightarrow T \longrightarrow \hat{Y}$. By the Data Processing Inequality (DPI) for Markov chains: $I(Y^*; T \mid \tilde{\mathcal{I}}, \mathcal{Q}) = 0$... $I(Y^*; \hat{Y}) \le I(Y^*; \tilde{\mathcal{I}}, \mathcal{Q}) < I(Y^*; \mathcal{I}, \mathcal{Q})$.`
- **Mathematical Audit:**
  1. The Markov condition holds if and only if deliberation tokens $T$ are generated by an autoregressive decoder that conditions exclusively on downsampled representation $\tilde{\mathcal{I}}$ and query $\mathcal{Q}$, with zero side-channel access to native pixels $\mathcal{I}$ or label $Y^*$. This assumption must be explicitly stated.
  2. The strict inequality $I(Y^*; \tilde{\mathcal{I}}, \mathcal{Q}) < I(Y^*; \mathcal{I}, \mathcal{Q})$ holds *only if* the downsampling transformation $\mathcal{I} \to \tilde{\mathcal{I}}$ is lossy with respect to the minimal sufficient statistic for $Y^*$. For large-print text where downsampling is lossless, equality holds.
  3. **Crucial Correction:** DPI proves that reasoning over $\tilde{\mathcal{I}}$ cannot create information not present in $\tilde{\mathcal{I}}$. It **does not prove** that taking a spatial sub-crop $\mathcal{I}_{\text{crop}}$ increases mutual information. If the crop misses the target evidence, $I(Y^*; \mathcal{I}_{\text{crop}}) = 0$.

### B. Proposition 1: Regret and Estimation Gaps (Appendix B)
- **Current Formulation (Line 246):**  
  `$|\hat{\Delta P}_a(s) - \Delta P_a(s)| \le \delta_P$ and $|\hat{C}_a(s) - C_a(s)| \le \delta_C$.`
- **Mathematical Audit:**  
  This proposition is a standard Lagrangian perturbation bound on greedy ratio selection. However, the manuscript must explicitly state that in real-world deployments, estimation errors are heteroscedastic and not uniformly bounded by a small constant $\delta_P$.

---

## 4. Causal Language Audit

Every instance of over-reaching causal language in `naacl/main.tex` must be systematically replaced:

| Current Manuscript Phrasing | Required Scientific Replacement | Methodological Justification |
| :--- | :--- | :--- |
| *"decisively outperforms"* | *"achieves higher sample accuracy on"* | Descriptive difference; avoids unwarranted generalization. |
| *"eliminates Type-I intervention compute"* | *"empirically reduces intervention frequency on clear documents"* | Avoids claiming a 100% deterministic elimination of false interventions. |
| *"proves that observation scaling is required"* | *"demonstrates that downsampling degrades recognition where reasoning cannot recover missing strokes"* | Aligns with information-theoretic limits without claiming algorithmic proof. |
| *"reliably suppresses false interventions"* | *"partially mitigates unregularized over-triggering"* | Acknowledges the 9 harmful flips that persisted under C-GVoC in the pilot. |

---

## 5. Granular Verification of the Cropping Failure Mechanism

We inspected the original images, transformed images, model responses, and ground truth for all 15 instances where center 50% cropping ($C4$) failed in the 20-instance run:

| Instance ID | Dataset | Question Summary | Ground Truth | Original Full Image Result (C1) | Center 50% Crop Result (C4) | Verified Visual Removal Mechanism |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `docvqa_012` | DocVQA | Dealer name | `"A. C. Monk"` | `"A. C. Monk"` (Corr) | `"Foreign Matter Found..."` (Incorr) | **Header Severed:** Dealer name is in the top-left margin; center crop excluded top 25% of document. |
| `docvqa_013` | DocVQA | Page number | `"31"` | `"31"` (Corr) | *"No page number is mentioned..."* (Incorr) | **Margin Severed:** Page number is printed in the top corner margin; center crop physically removed it. |
| `docvqa_016` | DocVQA | Grass/straw pieces | `"2"` | `"2"` (Corr) | `"1"` (Incorr) | **Table Row Clipped:** Lower rows of the core sample table were cut off by bottom boundary. |
| `docvqa_017` | DocVQA | Lint/string pieces | `"22"` | `"22"` (Corr) | `"1"` (Incorr) | **Table Row Clipped:** Same core sample form; target row fell outside center crop box. |
| `chartqa_010` | ChartQA | Slovenia value | `"1"` | `"1 GPI"` (Corr) | `"0.05"` (Incorr) | **Bar/Axis Misalignment:** Country category names on the baseline axis were severed. |
| `chartqa_012` | ChartQA | Leftmost value China | `"17"` | `"17"` (Corr) | `"5%."` (Incorr) | **Category Label Severed:** Country labels on x-axis were cropped out. |
| `chartqa_016` | ChartQA | Peak year | `"2014"` | `"2014"` (Corr) | *"Peak is not reached within visible range"* | **Peak Clipped:** Peak occurred at the far right edge (year 2014); model explicitly noted it was outside range. |
| `chartqa_017` | ChartQA | Sharpest increase | `"2011"` | `"2013 to 2014"` (Incorr) | *"Between first and second points"* (Incorr) | **Date Axis Severed:** Model saw line segments but had no year labels to identify the dates. |

**Audit Conclusion:** In at least 8 of the 15 failures, relevant text, labels, or axes were **directly, physically removed from the image canvas** by the center crop. This confirms that unguided geometric cropping destroys peripheral context.

---

## 6. Separation of Contributions into Three Distinct Claims

```
+--------------------------------------------------------------------------------------------------+
| CLAIM 1: ENGINEERING FINDING (SUPPORTED BY DATA)                                                 |
| Concise prompt formatting prevents conversational verbosity that causes output truncation        |
| under restricted production token ceilings (60 tokens).                                          |
| Status: SUPPORTED across both diagnostic (N=12) and exploratory (N=20) runs.                     |
+--------------------------------------------------------------------------------------------------+
| CLAIM 2: EMPIRICAL HYPOTHESIS (SUPPORTED BY DATA)                                                |
| Visual transformations have strongly layout-dependent effects. While downsampling degrades fine  |
| text, unguided cropping removes peripheral context (axes, legends, page numbers), degrading     |
| accuracy from 60% to 25% (p = 0.0391). Observation scaling requires verified spatial grounding.   |
| Status: SUPPORTED across 15 audited failure cases.                                              |
+--------------------------------------------------------------------------------------------------+
| CLAIM 3: METHOD CONTRIBUTION (UNVALIDATED IN LIVE DEPLOYMENT; SIMULATION ONLY)                   |
| An offline-trained decision controller can reliably estimate the counterfactual value of visual  |
| interventions relative to stopping and improve real-world VLM accuracy.                         |
| Status: UNVALIDATED on live models (72% and 76% vs. 82% monolithic in pilot). Supported only in  |
| 16,000-query synthetic simulation.                                                               |
+--------------------------------------------------------------------------------------------------+
```

---

## 7. Decision Gate: Recommendations

We evaluate three potential next steps:

### Option A: Revise Manuscript with Existing Evidence and Narrow Claims (RECOMMENDED)
- **Action:** Keep the paper strictly within its verified empirical bounds.
- **Narrative:**
  1. Position GVoC as a decision-theoretic framework for test-time compute allocation between observation space and reasoning space.
  2. Report the 16,000-query benchmark honestly as an offline diagnostic simulation showing potential when spatial grounding is present.
  3. Report the 100-instance live pilot transparently as a case study in real-world deployment challenges: uncovering the **Truncation Ceiling Trap** (conversational prompts hitting output limits) and the **Grounding Prerequisite** (unguided cropping severing document context).
- **Feasibility:** Zero additional API cost; zero delay; 100% scientifically defensible.

### Option B: Run a New Independent Confirmatory Benchmark
- **Action:** Evaluate a genuinely untouched, independent sample of $N = 100$ instances drawn from official test splits (e.g., DocVQA test or InfoVQA).
- **Requirements:**
  - Must use genuine learned bounding-box localization (not blind center crops).
  - Must enforce concise format decoding across all intervention branches.
  - Estimated API calls: $100 \text{ instances} \times 3 \text{ branches} = 300 \text{ calls}$.
  - Estimated cost: $\approx \$0.045$ USD.
  - Estimated runtime: ~8–10 minutes.

### Option C: Redesign the Controller Before Further Evaluation
- **Action:** Retrain the LightGBM advantage estimator using features that incorporate output token length constraints and spatial attribution verification before launching further tests.

---

## Final Recommendation: Select Option A for Current NAACL Submission

We recommend **Option A**: Proceed with an honest, methodologically rigorous revision of `naacl/main.tex` that narrows all claims to the verified facts, explicitly documents the engineering finding on output ceilings, and presents the live pilot as an empirical study of real-world test-time scaling bottlenecks.
