# Adversarial Initial Scientific Review (Pre-Revision Audit)

**Reviewer:** Agent C (Adversarial Scientific Reviewer)  
**Target Paper:** *Think Longer or Look Closer? Test-Time Scaling for Visual Document Understanding*  
**Date:** October 11, 2026  
**Initial Recommendation:** **STRONG REJECT (Prior Draft) $\longrightarrow$ CONDITIONAL PIVOT REQUIRED**

---

## 1. Summary of Prior Claims vs. Physical Reality

The baseline paper attempts to claim a sweeping breakthrough: that an adaptive controller (GVoC / C-GVoC) can dynamically solve test-time compute allocation in visual document understanding, outperform multi-agent debate (MACT) by +5.8% at -23.7% tokens, and preserve optimal stopping accuracy on live models with zero cost overhead.

**As a skeptical NAACL reviewer, I find that the baseline paper's headline narrative collapses upon inspecting the actual data files:**

1. **The 16,000-Query Benchmark is Synthetic Simulation, Not Live Inference:**
   The paper's headline Table 1 claims 16,000 document queries across Pixtral 12B, Qwen2-VL 27B, GPT-OSS 120B, and Gemini 3.6 Flash. Inspection of `gvoc_engine/benchmark/dataset_generator_16k.py` and `gvoc_evaluation.db` proves this is an **offline simulation using modeled state transitions and synthetic noise perturbations**. It does not represent 16,000 live foundation model API calls.
2. **The Live Pilot Contradicts the Superiority Narrative:**
   When tested on genuine live models (`pixtral-12b-2409`, $N=100$), monolithic zero-shot direct inference achieved **82.0% accuracy**. Unregularized GVoC collapsed to **72.0% accuracy** (-10.0 points, $p = 0.0129$) while inflating tokens by +101% (2,889 vs. 1,428 tokens). C-GVoC achieved **76.0% accuracy** (-6.0 points, $p = 0.1460$) with +17% token overhead. Calling this "preserving optimal stopping accuracy with zero overhead" is scientifically indefensible.
3. **The 20-Instance "Confirmatory" Sample Has Zero Independence:**
   Prior research notes claimed that a 20-instance experiment independently validated the method. An exact audit of question IDs and image hashes (`confirmatory_overlap_audit.csv`) reveals that **20 out of 20 instances were drawn directly from the pilot dataset**, with 3 direct overlaps with the diagnostic probe, and only 10 unique images in total. This is an exploratory pilot probe, not an independent confirmation.
4. **The Cropping Mechanism is Fragile and Ungrounded:**
   In the 20-instance probe, center 50% cropping achieved only **25.0% accuracy** vs. **60.0%** for downsampled full images ($p = 0.0391$). Physical image inspection proved that blind cropping cut off headers, dealer names, page numbers, and axis labels. Observation scaling fails catastrophically without learned spatial localization.
5. **The Epistemic Uncertainty Proxy is Anti-Correlated with Error:**
   The paper claims conservative risk control via an epistemic dispersion estimate $\hat{\sigma}$. In reality, telemetry logs (`audit_uncertainty_proxy.py`, $N=200$) show that $\hat{\sigma}$ has a **statistically significant negative correlation with prediction error** ($r = -0.2173, p = 0.0020$). Describing this as calibrated epistemic uncertainty is factually false.
6. **Theoretical Overclaiming on DPI and Regret:**
   Theorem 1 invokes the Data Processing Inequality as if it proves that GVoC succeeds. DPI proves that reasoning over blurred inputs cannot recover missing information; it does *not* prove that a cropping policy will capture the necessary pixels. Furthermore, Proposition 1 assumes uniform estimation bounds $\delta_P$, which are violated in empirical model telemetry.

---

## 2. Path Forward & Rejection Remedy

The paper cannot be saved as an unconstrained "novel controller that dominates all baselines." It **can** be saved as a high-integrity, scientifically illuminating paper if the authors execute a rigorous pivot:

1. **Re-frame the paper honestly:** Position GVoC as a decision-theoretic framework for test-time compute allocation between observation space and reasoning space.
2. **Report the 16k benchmark as an offline diagnostic simulation** that establishes the theoretical potential of observation scaling when spatial grounding is present.
3. **Report the live pilot transparently as an empirical case study** uncovering the two primary bottlenecks in real-world deployment:
   - *The Truncation Ceiling Trap:* Conversational prompts exhausting completion budgets and cutting off reasoning.
   - *The Grounding Prerequisite:* Unguided geometric crops destroying peripheral context ($p = 0.0391$).
4. **Retract all claims of zero-cost preservation, calibrated epistemic guarantees, and independent confirmation.**
5. **Qualify Theorem 1 and Proposition 1** with explicit Markov assumptions and sensitivity boundaries.

If these corrections are executed with complete transparency, the paper transforms from an overclaiming target for rejection into a rigorous, cautionary, and valuable NAACL contribution.
