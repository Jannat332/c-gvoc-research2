# Final Research Decision & Contribution Boundary

**Date:** October 10, 2026  
**Document:** `research/FINAL_RESEARCH_DECISION.md`  
**Team:** Principal Investigator, Literature Auditor, Adversarial Reviewer, Mathematical Auditor

---

## 1. Primary Research Question

> **Can allocating test-time compute to *observation space* (acquiring higher-fidelity visual evidence) outperform scaling in *reasoning space* (chains of thought or multi-agent debate) when visual resolution is the bottleneck in document understanding, and can a cost-normalized decision controller effectively balance this trade-off?**

---

## 2. Novelty Verdict & Literature Boundary

### Competing Paradigm: Procedural Multi-Agent Scaling (MACT)
The closest competing state-of-the-art framework is **MACT** (*Yu et al., arXiv:2508.03404v2*).
- **What MACT does:** Decomposes document QA into four agents ($A_{\text{plan}}, A_{\text{exe}}, A_{\text{judg}}, A_{\text{ans}}$) and scales test-time compute by generating parallel planning paths, executing step-wise plans, and looping through judgment and self-correction up to $N_c = 3$ times.
- **The Critical Gap in MACT:** MACT scales test-time compute *exclusively over static, fixed visual inputs*. If tiny numbers, decimal points, table borders, or footnotes were blurred during image downsampling, MACT loops through planning, execution, and judgment agents on the corrupted representation, burning tokens without access to the missing signal.
- **Our Residual Novelty:** GVoC establishes that **test-time compute can be spent in observation space**. Rather than debating over static blurry images, GVoC treats high-resolution re-grounding as an active test-time action and introduces **Grounded Value-of-Compute (GVoC)**—weighing estimated marginal correctness gain against token cost—to decide when looking closer is worth the compute.

### Other Competing Lines:
1. **Test-Time Compute in LLMs (Snell et al., 2024; Tong et al., 2026):** Scaled search, beam search, and best-of-N across reasoning chains, but restricted to textual reasoning without visual evidence acquisition.
2. **High-Resolution Document Architectures (U-Reader, LLaVA-NeXT):** Process all documents at high resolution via uniform grid slicing, incurring massive token costs even on trivial queries. GVoC is an adaptive policy that intervenes only when needed.
3. **Multi-Agent Tool Use (VisDocAgent):** Routes tools heuristically via prompt instructions without counterfactual advantage estimation or cost normalization.

---

## 3. Separation of the Three Core Claims

To maintain total scientific integrity, our findings are partitioned into three cleanly categorized claims:

1. **Engineering Finding (Empirically Supported):**
   *Under constrained production token budgets (e.g. 60 tokens), conversational prompts cause catastrophic output truncation (up to 100% on ChartQA), destroying accuracy. Format-constrained concise decoding eliminates truncation and restores accuracy using minimal tokens.*
2. **Empirical Hypothesis (Empirically Supported):**
   *Visual transformations have strongly layout-dependent effects. While downsampling degrades fine character strokes, unguided geometric cropping destroys peripheral context (axes, column headers, page numbers), degrading accuracy from 60.0% to 25.0% ($p = 0.0391$). Therefore, observation-space scaling requires verified spatial grounding.*
3. **Method Contribution (Validated in Simulation; Real-World Bottlenecks Identified in Pilot):**
   *We formalize Grounded Value-of-Compute (GVoC), a decision-theoretic framework for test-time compute allocation between observation space and reasoning space. In an offline 16,000-query benchmark simulation with grounded actions, GVoC reaches 70.2% accuracy (improving over MACT by +5.8 points while using 23.7% fewer tokens). In a live 100-instance deployment on Mistral Pixtral-12B, unregularized intervention risks over-triggering, while conservative penalization partially mitigates harm—empirically identifying the Truncation Ceiling Trap and the Grounding Prerequisite as essential engineering lessons for future test-time systems.*

---

## 4. Rejected Hypotheses & Retracted Claims

- **RETRACTED:** Claim that *"C-GVoC preserves optimal stopping accuracy with zero cost overhead."* (Raw live pilot showed 76.0% vs 82.0% monolithic accuracy and +17% token overhead; $p=0.1460$).
- **RETRACTED:** Claim that *"The 20-instance confirmatory run independently validated observation scaling."* (Audit proved 20/20 instances overlap with the pilot; relabeled strictly as exploratory).
- **RETRACTED:** Claim of a novel architecture called *"D-BOS"*. (Format-enforced decoding is standard direct prompting, not a new neural architecture).
- **QUALIFIED:** Data Processing Inequality (Theorem 1). Stated strictly as an upper bound on reasoning over blurry inputs under explicit Markov assumptions ($Y^* \to X_{\text{high}} \to X_{\text{low}} \to T$), not as an algorithmic proof that cropping succeeds.
- **QUALIFIED:** Proposition 1. Stated as a stylized perturbation bound under assumed uniform estimation error, not a distribution-free PAC guarantee.

---

## 5. Execution Decision: Option A (Submission with Narrowed, Verified Claims)

We proceed with **Option A**: Revise `naacl/main.tex` and the supporting materials to present an airtight, submission-ready short paper that reports all verified simulation gains honestly, presents the live pilot as an illuminating real-world study of test-time scaling bottlenecks, and avoids all overclaiming.
