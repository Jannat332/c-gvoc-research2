# Decision Gate: Go / No-Go Recommendation for NAACL Manuscript

**Auditors & Research Team:**
- **Empirical Methodology Auditor**
- **ML Systems Engineer**
- **Critical Paper Reviewer**

**Date:** October 10, 2026  
**Artifact Scope:** Comprehensive review of raw evidence in `live_evaluation.db`, `diagnostic_evaluation.db`, `confirmatory_evaluation.db`, `confirmatory_overlap_audit.csv`, and `naacl/main.tex`.

---

## 1. Decision Gate Verdict

$$\mathbf{VERDICT: \quad NO\text{-}GO \quad ON \quad CLAIM \quad EXPANSION}$$
$$\mathbf{VERDICT: \quad GO \quad ON \quad HONEST \quad EMPIRICAL \quad REFRAMING}$$

---

## 2. Forensic Audit Findings Linking to Raw Evidence

### A. Evaluation-Set Contamination
- **Raw Evidence:** In [`confirmatory_overlap_audit.csv`](file:///c:/Users/user/Desktop/recent_projects/ESWA_ehte/discovery/live_validation/confirmatory_overlap_audit.csv), **20 out of 20 instances (100.0%)** evaluated in the confirmatory run were drawn directly from the initial 100-instance pilot dataset.
- **Diagnostic Overlap:** Exactly 3 instances (`chartqa_014`, `chartqa_017`, `chartqa_018`) directly overlapped with the 12-instance diagnostic probe, and 3 more (`chartqa_015`, `chartqa_016`, `chartqa_019`) shared identical document image hashes with diagnostic instances.
- **Severe Image Clustering:** The 20 questions span only **10 unique visual documents**.
- **Audit Conclusion:** **Zero instances can be classified as an untouched or independent evaluation set.** Any claim that the confirmatory experiment independently validated generalization is factually unsupported.

### B. Causal Confounding in Condition Contrasts
- **Raw Evidence:** In [`causal_claim_audit.md`](file:///c:/Users/user/Desktop/recent_projects/ESWA_ehte/discovery/live_validation/causal_claim_audit.md), the initial claim that Contrast C4 vs. C3 proved "observation scaling beats reasoning scaling" was severely confounded, varying image transformation, prompt style, and generation budget simultaneously.
- **Clean Contrast Finding:** When prompt style and budget are held strictly identical (C4 vs. C2 at 60 tokens, concise prompt), blind center-cropping achieved **only 25.0% accuracy** compared to **60.0%** for the full downsampled image ($p = 0.0391$ McNemar exact test).
- **Audit Conclusion:** Naive geometric cropping catastrophically degrades document and chart understanding by severing peripheral axes, legends, headers, and footers. Visual intervention requires verified spatial localization.

### C. Statistical Uncertainty and Sample Size Boundaries
- **Raw Evidence:** In [`corrected_statistical_report.md`](file:///c:/Users/user/Desktop/recent_projects/ESWA_ehte/discovery/live_validation/corrected_statistical_report.md), with $N = 20$ queries and $N_{\text{eff}} \approx 10$ unique images, statistical power is restricted to detecting only massive effect sizes ($\ge 35\%$).
- **Planned Contrasts After Bonferroni Adjustment:** The prompt-style contrast (C1 vs. C5, $p = 0.375$) and the sensory degradation contrast (C1 vs. C2, $p = 0.375$) do not achieve significance after adjustment. Non-significance reflects low statistical power, not equivalence.

### D. Literature Novelty Boundaries
- **Raw Evidence:** In [`novelty_claim_audit.md`](file:///c:/Users/user/Desktop/recent_projects/ESWA_ehte/discovery/live_validation/novelty_claim_audit.md), concise prompt formatting is standard practice in NLP and cannot be framed as a novel architecture ("D-BOS"). The Data Processing Inequality is an upper bound on mutual information, not a guarantee that a specific cropping controller will improve accuracy.

---

## 3. Explicit Policy on Manuscript Claims

### Mandatory Claims to Prohibit (DO NOT INCLUDE):
1. **DO NOT** claim that C-GVoC *"preserves optimal stopping accuracy with zero cost overhead."* In the raw 100-instance pilot, C-GVoC accuracy is 76.0% (vs. 82.0% monolithic) with +17% cost overhead.
2. **DO NOT** promote "Dual-Budget Observation Scaling (D-BOS)" as a novel standalone method.
3. **DO NOT** cite the 20-instance confirmatory run as an "independent confirmatory benchmark."
4. **DO NOT** cite the Data Processing Inequality as a proof of GVoC's empirical success.
5. **DO NOT** claim that $\hat{\sigma}_a(s)$ provides "calibrated Bayesian epistemic uncertainty" or theoretical PAC/LCB regret bounds.

### Defensible, Evidence-Backed Claims to Maintain:
1. **Formalize the Observation vs. Reasoning Dichotomy:** Articulate that test-time compute in multimodal models must target the true bottleneck: sensory acquisition for missing pixels, reasoning tokens for cognitive logic.
2. **Decision-Theoretic Allocation:** Position GVoC as a framework estimating counterfactual marginal advantage ($\Delta P_a(s)$) over stopping normalized by token cost.
3. **Document the Truncation Ceiling Trap:** Present the empirical finding that conversational intervention instructions trigger verbosity that hits production token ceilings, necessitating concise output constraints.
4. **Document the Grounding Prerequisite:** Show empirically that observation scaling requires verified spatial localization, as unguided crops destroy peripheral document context ($p < 0.04$).
5. **Transparent Dual Reporting:** Present the 16,000-query benchmark explicitly as an offline diagnostic simulation, paired transparently with the 100-instance live pilot outcomes.

---

## 4. Final Strategic Recommendation

Do not rush to expand claims or manufacture artificial novelty. The strongest, most publishable version of this paper is one that is **methodologically rigorous, honest about live-pilot failure modes, and grounded in reproducible empirical facts**. Reviewers at top NLP venues respect papers that discover and honestly analyze real-world system bottlenecks over papers with over-engineered, unverified claims.
