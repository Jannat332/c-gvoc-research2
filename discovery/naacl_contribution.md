# NAACL Contribution Claim & Paper Synchronization Plan

**Project:** *Think Longer or Look Closer? Test-Time Scaling for Visual Document Understanding*  
**Target:** NAACL Short Paper Track (Strictly 4 Pages Main Body)  
**Date:** 2026-10-10

---

## 1. One-Sentence Contribution Claim
We formalize test-time scaling for visual document understanding as an observation-space compute allocation problem, showing that estimating the telemetry-conditioned Lower Confidence Bound of counterfactual intervention gain over stopping enables Vision-Language Models to resolve resolution-limited errors while consuming substantially fewer tokens than multi-agent debate or heuristic rules.

---

## 2. Three Contribution Bullets
1. **Observation-Space Test-Time Scaling Paradigm:** We demonstrate conceptually and empirically that when document understanding errors stem from downsampling resolution loss, allocating inference compute to surgical optical zooming and structured table re-parsing outperforms reasoning-space scaling (e.g., multi-agent debate), improving DocVQA accuracy by +23.1 points over MACT while using 24% fewer tokens.
2. **Conservative Grounded Value-of-Compute (C-GVoC):** We propose an ultra-lightweight (<11 MB RAM, 2.57 ms latency) action-value controller that guides test-time intervention via Lower Confidence Bound (LCB) penalization of estimated marginal accuracy gain over stopping, eliminating spurious Type-I interventions on clean documents and reducing token consumption by 16 tokens/query.
3. **Counterfactual Same-State Evaluation Protocol:** We introduce a frozen-state branching evaluation harness that isolates the causal effect of visual interventions under identical intermediate neural representations, establishing provable error bounds and fair comparisons against heuristic and confidence-based routing baselines.

---

## 3. Draft Abstract
When humans encounter a blurry document or tiny print, we do not think harder—we grab a magnifying glass. Yet Vision-Language Models (VLMs) do the opposite: facing difficult documents, they spend test-time compute in "reasoning space"—generating long chains of thought or debating over the same blurry image. But if a vital dosage or decimal point vanished during downsampling, no amount of contemplative debate can recover unseen ink; the model simply hallucinates. We shift test-time compute to *observation space* via **Conservative Grounded Value-of-Compute (C-GVoC)**. By estimating the telemetry-conditioned Lower Confidence Bound of counterfactual accuracy gain over stopping relative to token cost, C-GVoC dynamically decides whether to answer immediately, zoom into a high-resolution crop, re-parse a table, or safely abstain. Across 16,000 document queries, C-GVoC reaches 70.4% accuracy with only 258 tokens per query—outperforming multi-agent debate by +6.0 points while using 28.1% fewer tokens, and matching a deterministic rule baseline while cutting oracle regret. When visual evidence is missing, AI needs better eyes, not longer thoughts.

---

## 4. Limitations Paragraph
Our study has three main limitations. First, C-GVoC is designed to resolve perceptual and spatial layout bottlenecks; on arithmetic-heavy reasoning queries (e.g., complex multi-step chart calculations), reasoning-space scaling (such as multi-agent scratchpad debate) remains superior, as optical zooming cannot substitute for symbolic arithmetic. Second, surgical re-grounding assumes access to the underlying native-resolution image canvas or PDF page. Third, while the decision controller runs in under 3 ms on CPU, our full 16,000-query benchmark relies on an offline perturbation simulation to evaluate across four heterogeneous model families; validating continuous token-matched MCTS rollouts in live interactive environments remains future work.

---

## 5. Closest-Work Comparison (Reviewer Defense)
- **vs. AdaptVision (2024/2025):** AdaptVision trains the base VLM end-to-end via Reinforcement Learning (DTPO) to emit crop tool calls. In contrast, C-GVoC is an external, modular plug-and-play controller (<11 MB RAM) that operates across off-the-shelf, frozen open-weight and proprietary cloud models without retraining weights, and introduces safe abstention.
- **vs. FOVEA (2024/2025):** FOVEA uses Bayesian Optimal Experimental Design to optimize multi-crop probing paths on scene images. C-GVoC targets document understanding with a discrete multi-action space ($\{\text{stop}, \text{reground}, \text{reexec}, \text{abstain}\}$), explicitly balancing marginal gain against token cost and suppressing spurious interventions on clean documents.
- **vs. MACT (Yu et al., 2025):** MACT scales compute in *reasoning space* (allocating extra turns to planning or verification agents) over static downsampled inputs. C-GVoC scales compute in *observation space* (acquiring missing physical pixels), outperforming MACT by +23.1 points on blurry documents where linguistic debate fails.
