# Independent Novelty & Literature Audit

**Reviewer:** Agent B (Independent Novelty Reviewer)  
**Date:** October 11, 2026  
**Location:** `research_revision/NOVELTY_AUDIT.md`

---

## 1. Literature Scope & Primary Sources Examined

We performed an independent primary-source review of competing test-time scaling, document AI, and visual acquisition frameworks:

1. **MACT (Base Baseline):** *Yu et al. (arXiv:2508.03404v2, August 2025)* — "Visual Document Understanding and Reasoning: A Multi-Agent Collaboration Framework with Agent-Wise Adaptive Test-Time Scaling".
2. **Textual Test-Time Scaling:** *Snell et al. (arXiv:2408.03314, 2024)* — "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters"; *Tong et al. (arXiv:2601.08743, 2026)* — "Scaling Test-Time Compute without Architecture Modifications".
3. **High-Resolution Document Architectures:** *Ye et al. (EMNLP 2023)* — "U-Reader: Universal OCR-free Visually-situated Language Understanding"; *Liu et al. (2024)* — "LLaVA-NeXT"; *Blecher et al. (2023)* — "Nougat".
4. **Tool-Augmented Document Agents:** *Hu et al. (arXiv:2602.04910, 2026)* — "VisDocAgent-Bench"; *Rahman et al. (2026)* — "Capability-Routed Agent Teams".
5. **Decision Theory & Selective Prediction:** *Howard (1966)* — "Information Value Theory"; *Horvitz (1988)* — "Reasoning about Computational Resource Constraints"; *Russell & Wefald (1991)* — "Do the Right Thing"; *Geifman & El-Yaniv (2017)* — "Selective Classification".

---

## 2. In-Depth Comparison: GVoC vs. MACT (Primary Competitor)

| Evaluation Dimension | MACT (*Yu et al., 2025*) | GVoC (*This Work*) | Defensible Scientific Distinction |
| :--- | :--- | :--- | :--- |
| **Problem Formulation** | Procedural multi-agent scaling for document understanding. | Decision-theoretic test-time compute allocation between observation and reasoning. | GVoC formalizes observation vs. reasoning trade-offs. |
| **Observation Representation** | **Static downsampled image** $D = \{v_1, \dots, v_n\}$ kept fixed across all steps. | Dynamic: initial overview $I_{\text{low}}$ plus **targeted high-resolution crop** $I_{\text{crop}}$ on demand. | **Major Algorithmic Distinction:** GVoC alters physical visual fidelity; MACT cannot. |
| **Action Space** | Planning path generation ($N_p$), tool execution, judgment critique, answer synthesis. | Stop ($a_{\text{stop}}$), Re-Ground Crop ($a_{\text{reground}}$), Re-Execute Table ($a_{\text{reexec}}$), Abstain ($a_{\text{abstain}}$). | Discrete operational actions specifically targeting visual resolution bottlenecks. |
| **Inference Loop & Cost** | Up to $N_c = 3$ correction loops across 4 agents ($4 \text{ to } 12$ calls). Unbounded tokens. | At most 1 targeted visual intervention (max 2 calls). Terminated by cost-normalized gating. | GVoC bounds inference latency and normalizes by token cost. |
| **Decision Rule** | Heuristic judgment agent passing/failing execution steps. | Cost-normalized Intervention Value: $\mathcal{V}(s, a) = (\hat{\Delta P}_a - \lambda \hat{\sigma}_a) / (C_a + \epsilon)$. | GVoC optimizes expected correctness gain per token spent. |
| **Failure Mode** | Deliberates endlessly over blurred text, producing convincing hallucinations. | Crop failure if spatial grounding misses target coordinates; prompt truncation if verbose. | Disclosed failure boundaries. |

---

## 3. Comparison with Other Literature Streams

### A. Textual Test-Time Scaling (Snell et al., 2024; Tong et al., 2026)
- **Prior Work:** Scales search, verifiers, and beam search over language tokens. Assumes the entire problem context is textually complete and fully observable.
- **GVoC Distinction:** Multimodal document understanding is fundamentally partially observable due to optical downsampling. Increasing reasoning tokens over a blurred image cannot recover unseen pixels. GVoC establishes that compute must be spent in **observation space**.

### B. High-Resolution Document Architectures (U-Reader, LLaVA-NeXT)
- **Prior Work:** Slices *every* document image into a dense grid of high-resolution patches, inflating token counts by $4\times\text{--}16\times$ even for simple documents.
- **GVoC Distinction:** GVoC is an **adaptive test-time policy** that evaluates full-resolution crops only when the expected correctness gain justifies the token expense, stopping immediately on clear pages.

### C. Tool-Using Agents (VisDocAgent, ViperGPT)
- **Prior Work:** Relies on unstructured LLM prompts to decide whether to call external OCR, cropping, or Python scripts. No cost normalization or counterfactual advantage training.
- **GVoC Distinction:** GVoC uses offline same-state counterfactual branching to learn whether an intervention actually improves accuracy relative to stopping.

---

## 4. Novelty Verdict and Permitted Claims

```
+---------------------------------------------------------------------------------------------------------+
| NOVELTY VERDICT: GENUINE ALGORITHMIC DISTINCTION SURVIVES AUDIT                                         |
+---------------------------------------------------------------------------------------------------------+
| 1. PERMITTED NOVELTY CLAIM:                                                                             |
|    GVoC is the first framework to formalize test-time compute allocation between observation space     |
|    (high-resolution visual resampling) and reasoning space (linguistic deliberation) via a cost-        |
|    normalized counterfactual Value-of-Compute ratio.                                                    |
|                                                                                                         |
| 2. FORBIDDEN OVERCLAIMS:                                                                                |
|    - Do NOT claim that GVoC is the first method to crop images (U-Reader, VOILA crop images).          |
|    - Do NOT claim that GVoC "dominates all baselines on live models" (live pilot had negative gaps).    |
|    - Do NOT claim that GVoC's uncertainty proxy is a calibrated Bayesian guarantee.                     |
|    - Do NOT claim that DPI proves GVoC's superiority over all reasoning architectures.                  |
+---------------------------------------------------------------------------------------------------------+
```
