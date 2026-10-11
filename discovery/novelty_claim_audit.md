# Novelty Claim Audit: Primary Source Verification and Theoretical Boundaries

**Auditor:** Critical Paper Reviewer & Empirical Methodology Auditor  
**Date:** October 10, 2026  
**Artifact Scope:** Primary source verification of competing literature, theoretical bounds, and defensible novelty claims

---

## 1. Primary Source Verification: Distinguishing Fact from Interpretation

To ensure research integrity, we re-audited every citation in `literature_novelty_matrix.md` against its original published manuscript to separate **documented findings** from **interpretive claims**.

### A. Snell et al. (2024) — *Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters*
- **Primary Source Finding:** Focuses strictly on autoregressive text LLMs on MATH and GSM8K. Shows that scaling test-time compute via best-of-N sampling, beam search against a process reward verifier, and revision loops can match or outperform larger models.
- **Audited Distinction:** Snell et al. **never evaluate multimodal models or visual documents**. Claiming that Snell et al. "fail at vision" is an inaccurate interpretation; vision was simply out of scope.
- **Accurate Characterization:** Snell et al. established test-time compute scaling laws for purely symbolic text reasoning, leaving multimodal sensory scaling unaddressed.

### B. Tong et al. (ICML 2026) — *Diversity Matters: Revisiting Test-Time Compute in Vision-Language Models*
- **Primary Source Finding:** Evaluates multimodal test-time scaling across MMBench, MathVista, and InfoVQA using temperature sampling and diverse prompt reformulations with majority voting.
- **Documented Evidence:** Shows that increasing sample rollouts over the *same static image* yields significant gains on complex reasoning (MathVista), but exhibits sharp plateauing on fine-grained visual perception.
- **Accurate Characterization:** Tong et al. directly confirm our foundational premise: repeated sampling over static visual inputs yields diminishing returns when fine perceptual evidence is ambiguous.

### C. Yu et al. (2025) — *MACT: A Multi-Agent Collaboration Framework with Agent-Wise Adaptive Test-Time Scaling*
- **Primary Source Finding:** Decomposes document reasoning into Planner, Executor, Judge, and Answering agents. Allocates compute by allowing the Judge agent to reject candidate outputs and trigger iterative multi-agent debate.
- **Audited Distinction:** Does MACT use visual tools or crops? **No.** MACT agents communicate exclusively via natural language text dialogue conditioned on the initial static visual encoding.
- **Accurate Characterization:** MACT scales test-time compute exclusively in conversational agent dialogue space (359–500 tokens per query). It cannot recover visual details lost during initial image encoding because no sensory re-acquisition occurs.

### D. Architectural High-Resolution Models (U-Reader, LLaVA-NeXT)
- **Primary Source Finding:** U-Reader (Ye et al., 2023) and LLaVA-NeXT (Liu et al., 2024) split images into multi-crop grids (AnyRes) to preserve native resolution.
- **Audited Distinction:** This is **static architectural tiling**, not dynamic test-time scaling. Every single document image—whether a simple one-sentence receipt or an intricate blueprint—receives the full grid of high-resolution tiles, incurring fixed, quadratic visual token overhead.
- **Accurate Characterization:** These architectures prove that high resolution is valuable, but do not provide a dynamic test-time mechanism to allocate resolution adaptively based on document clarity.

### E. Interactive Document Agents (VisDocAgentBench, DScale-Agent)
- **Primary Source Finding:** Provide models with tools to zoom, crop, and run OCR in open-ended ReAct loops.
- **Audited Distinction:** These frameworks rely on open-ended conversational prompting loops. They lack a formal Value of Information (VOI) framework, lack explicit cost normalization, and frequently consume 1,000–3,000 tokens per query with high tool-invocation error rates.

---

## 2. Deconstructing the Data Processing Inequality (DPI) Claim

In earlier drafts of `naacl/main.tex`, the Data Processing Inequality was cited as if it were a mathematical proof that our proposed method must succeed:

$$I(Y; \hat{Y}_{\text{reasoning}} \mid X_{\text{low}}) \le I(Y; X_{\text{low}})$$

### What the Data Processing Inequality Actually Proves:
1. Under the Markov chain $Y \to X_{\text{high}} \to X_{\text{low}} \to \hat{Y}$, the mutual information between the ground-truth document content $Y$ and any downstream generated tokens $\hat{Y}$ is strictly bounded by the mutual information preserved in the degraded image $X_{\text{low}}$.
2. If fine ink (e.g., a decimal point or tiny subscript) has zero mutual information with $X_{\text{low}}$ ($I(\text{ink}; X_{\text{low}}) = 0$), then no amount of autoregressive decoding over $X_{\text{low}}$ can recover it: $I(\text{ink}; \hat{Y}) = 0$. Generating tokens under this condition produces ungrounded hallucinations.

### What the Data Processing Inequality Does NOT Prove:
1. **DPI does NOT prove that a cropping policy will succeed.**  
   Information theory establishes an *upper bound* on information preservation, but does not guarantee that a specific spatial transformation preserves the *right* information.
2. **Empirical Refutation:**  
   As proven in our confirmatory experiment, blind center-cropping ($C4$) dropped accuracy to **25.0%** ($p = 0.0391$ vs. downsampled). Although $X_{\text{crop}}$ preserved high-resolution pixels, it destroyed the mutual information between the query and peripheral context ($I(Y; X_{\text{crop}}) < I(Y; X_{\text{low}})$).
3. **Manuscript Rule:**  
   The Data Processing Inequality must be presented strictly as a **motivational limit on reasoning over degraded inputs**, NOT as a theorem guaranteeing the effectiveness of GVoC or any cropping controller.

---

## 3. The True, Defensible Contribution of GVoC

When all inflated claims are removed, what remains as a novel, defensible, and scientifically sound contribution for NAACL?

1. **A Formalization of the Test-Time Scaling Dichotomy in Multimodal Models:**  
   We articulate and formalize the distinction between **Observation-Space Scaling** (acquiring high-resolution sensory evidence) and **Reasoning-Space Scaling** (generating internal scratchpad tokens). We show that test-time compute must target the actual bottleneck: visual evidence acquisition when downsampling destroys detail, and reasoning tokens when arithmetic or logic is the bottleneck.
2. **Counterfactual Value-of-Compute Allocation:**  
   Instead of heuristic agent loops or confidence routing (which triggers actions when the model is uncertain), GVoC estimates the **counterfactual marginal advantage** ($\Delta P_a(s)$) of physical observation actions relative to stopping, normalized by token cost.
3. **The Empirical Discovery of the Truncation Ceiling Trap:**  
   We document a critical, previously unaddressed failure mode in multimodal test-time scaling: visual intervention instructions inherently trigger conversational reasoning preambles that cause severe generation truncation under production token budgets (causing up to 100% failure on ChartQA) unless coupled with strict concise decoding constraints.
4. **The Grounding Prerequisite for Visual Interventions:**  
   We empirically demonstrate that observation-space scaling requires verified spatial localization; unguided cropping causes statistically significant performance degradation ($p < 0.04$) by destroying global document context.
