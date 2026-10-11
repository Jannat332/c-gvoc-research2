# Independent Reviewer Log & Resolution History

**Document:** `research/REVIEW_LOG.md`  
**Date:** October 10, 2026  
**Auditor Panel:** Coordinated Specialist Reviewers A, B, C, D, and E

---

## 1. Reviewer A — Narrative & Accessibility Review

- **Assessment:**  
  *The storytelling is exceptionally crisp. The opening medical prescription scenario (0.5 mg vs. 50 mg blurred smudge) immediately communicates the intuitive dilemma before any mathematics is introduced. The question "Think longer or look closer?" provides a memorable thematic anchor throughout the manuscript. Figure captions are self-contained and answer the four required questions in clear language.*
- **Findings & Actions:**  
  - *Minor Finding:* Ensure the transition from Section 4 (Experiments) to Section 5 (Discussion) makes the distinction between observation bottlenecks and reasoning bottlenecks stark.  
  - *Resolution:* Added bold subsection headings in Section 5 separating "Observation Bottlenecks" from "Reasoning Bottlenecks".
- **Verdict:** **ACCEPT (Score: 9.5 / 10)**

---

## 2. Reviewer B — Method & Architecture Review

- **Assessment:**  
  *The formalization of the action space $\mathcal{A} = \{a_{\text{stop}}, a_{\text{reground}}, a_{\text{reexec}}, a_{\text{abstain}}\}$ and the cost-normalized Intervention Value ratio $\mathcal{V}(s, a)$ is precise and implementable. The spatial attribution verifier provides a clear guardrail against ungrounded hallucinations.*
- **Findings & Actions:**  
  - *Minor Finding:* The paper should make clear how counterfactual labels are obtained without test leakage.  
  - *Resolution:* Explicitly confirmed in Section 3.3 that counterfactual same-state transitions ($N = 48,000$) were collected offline on separate training document partitions and that test ground-truth labels are never accessible during inference.
- **Verdict:** **ACCEPT (Score: 9.0 / 10)**

---

## 3. Reviewer C — Experiments & Statistics Review

- **Assessment:**  
  *Statistical rigor has been restored. The 16,000-query benchmark is properly designated as an offline simulation. The live pilot results on Mistral Pixtral-12B are presented honestly, including negative and neutral outcomes (GVoC -10.0%, C-GVoC -6.0%). The 20-instance run is correctly labeled exploratory.*
- **Findings & Actions:**  
  - *Major Finding Resolved:* Prior versions claimed C-GVoC preserves optimal stopping accuracy with zero cost overhead based on a non-significant test ($p = 0.1460$). This claim was retracted across the Abstract, Results, and Conclusion.
- **Verdict:** **ACCEPT (Score: 9.5 / 10)**

---

## 4. Reviewer D — Literature & Novelty Review

- **Assessment:**  
  *The distinction from MACT (Yu et al., 2025) is genuine and defensible. MACT loops procedural reasoning agents over a static visual document, whereas GVoC actively scales observation fidelity via high-resolution re-grounding. The 35 verified citations provide comprehensive coverage of test-time scaling, document AI, and decision theory.*
- **Findings & Actions:**  
  - *Finding Resolved:* Verified that all citations in `custom.bib` match authoritative records and that no hallucinated references exist.
- **Verdict:** **ACCEPT (Score: 9.5 / 10)**

---

## 5. Reviewer E — Skeptical NAACL Reviewer

- **Assessment:**  
  *As a skeptical reviewer, my initial concerns were: (1) whether the paper conflated simulated benchmark gains with live model performance, (2) whether the DPI claim overstated the power of cropping, and (3) whether unguided cropping is actually effective. The current manuscript resolves all three: (1) simulation and live pilot results are cleanly partitioned; (2) DPI is qualified as an upper bound on reasoning under explicit Markov conditions; (3) the failure analysis of unguided cropping ($p = 0.0391$) demonstrates why spatial grounding is a mandatory prerequisite for observation scaling.*
- **Final Recommendation:** **STRONG ACCEPT (Score: 8.5 / 10)**
