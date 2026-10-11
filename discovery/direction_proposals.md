# Exploration of Ten Distinct Research Directions

**Author:** Autonomous Research Team (Multi-Specialist Consortium)  
**Project:** *Think Longer or Look Closer? Test-Time Scaling for Visual Document Understanding*  
**Date:** 2026-10-10  
**Scope:** Exhaustive evaluation of 10 candidate methodological directions for the NAACL submission.

---

## Direction 1: Counterfactual Document Repair Planning (Damage vs. Repair Decomposition)

- **Research Hypothesis:** Modeling the probability of repair $P(\text{Repair}_a = 1 \mid s) = P(Y(a)=1 \mid Y(\text{stop})=0, s)$ and probability of harm $P(\text{Harm}_a = 1 \mid s) = P(Y(a)=0 \mid Y(\text{stop})=1, s)$ separately outperforms scalar net advantage $\Delta P_a(s)$.
- **Algorithm:**
  $$\hat{\Delta P}_a(s) = (1 - P_{\text{stop}}(s)) \cdot \hat{P}(\text{Repair}_a \mid s) - P_{\text{stop}}(s) \cdot \hat{P}(\text{Harm}_a \mid s).$$
  Score interventions using net expected utility penalized heavily by harm rate $\lambda_{\text{harm}}$.
- **Closest Prior Work:** Medical counterfactual treatment effect estimation (Shalit et al., 2017); Intervention repair in dialogue (He et al., 2022).
- **Exact Potential Contribution:** Prevents "do-no-harm" violations on high-confidence initial answers while maintaining high recovery on broken states.
- **Main Failure Mode:** On sparse counterfactual data where $Y(\text{stop})=1$, empirical damage events are rare (<2%), leading to degenerate variance in estimating $P(\text{Harm}_a)$.
- **Minimum Decisive Experiment:** Measure harm rate and net accuracy across the 40 paired scenarios with vs without decomposed harm estimation.
- **Data & Compute Requirements:** 160 paired outcomes (existing in `fresh_benchmark_loader.py`). Run time: <1 second on CPU.
- **Falsification Criterion:** If harm rate is already $< 2\%$ under clean-state suppression, decomposed harm estimation adds model complexity without improving Pareto efficiency.

---

## Direction 2: Calibrated Counterfactual Intervention Value (Uncertainty-Aware LCB)

- **Research Hypothesis:** Subtracting a calibrated lower confidence bound penalty $\kappa \cdot \hat{\sigma}_a(s)$ from estimated advantage suppresses spurious low-payoff interventions on clean documents, lowering token cost and oracle regret.
- **Algorithm:**
  $$\mathcal{V}_{\text{LCB}}(s, a) = \frac{\max\big(0,\; \hat{\Delta P}_a(s) - \kappa \cdot \hat{\sigma}_a(s)\big)}{C(s, a) + \epsilon}$$
  where $\hat{\sigma}_a(s)$ is estimated from state telemetry dispersion (consensus divergence, layout distortion).
- **Closest Prior Work:** Lower Confidence Bound in Bandits (Auer, 2002); Conservative Q-Learning (Kumar et al., 2020); FOVEA (2024).
- **Exact Potential Contribution:** Provides risk-bounded conservatism during inference-time tool usage without retraining foundation models.
- **Main Failure Mode:** Overly conservative $\kappa > 0.8$ over-suppresses beneficial repairs on borderline blurry documents, depressing overall accuracy.
- **Minimum Decisive Experiment:** Sweep $\kappa \in [0.0, 1.0]$ on validation fold (DocVQA + ChartQA), select $\kappa^*$, and evaluate regret on held-out test fold (TableBench + MMLongBench).
- **Data & Compute Requirements:** Reuses existing 40 paired benchmark scenarios. Run time: <1 second on CPU.
- **Falsification Criterion:** If $\kappa=0$ (uncalibrated point estimate) matches or beats $\kappa > 0$ on oracle regret on the held-out test fold, the LCB hypothesis is falsified.

---

## Direction 3: Sequential Value of Information (Multi-Step Finite Horizon POMDP)

- **Research Hypothesis:** A sequential controller that looks ahead across a 2-step horizon out-selects greedy 1-step $\Delta P / C$ selection when intermediate actions (e.g., zoom) reveal information that alters subsequent table-parsing choices.
- **Algorithm:**
  Solve a 2-step backward dynamic program on the discrete POMDP: $V^*(s_t) = \max_{a} [ R(s_t, a) + \mathbb{E}_{s_{t+1}}[V^*(s_{t+1})] ]$.
- **Closest Prior Work:** Partially Observable Markov Decision Processes (Kaelbling et al., 1998); Active Perception (Bajcsy, 1988); Tree search test-time scaling (Snell et al., 2024).
- **Exact Potential Contribution:** Formal multi-step optimality guarantee for test-time VDU reasoning.
- **Main Failure Mode:** In document VQA, $>90\%$ of errors are resolved in a single atomic intervention (e.g., zoom OR table re-execution); sequential chaining introduces cumulative token latency with minimal marginal accuracy gain.
- **Minimum Decisive Experiment:** Evaluate 2-step lookahead policy vs greedy 1-step policy on the 40 diagnostic scenarios.
- **Data & Compute Requirements:** Requires simulating $4 \times 4 = 16$ two-step branch combinations per scenario ($40 \times 16 = 640$ transitions).
- **Falsification Criterion:** If 2-step policy incurs $>150$ extra tokens for $<1\%$ accuracy improvement, sequential planning is inefficient for short-horizon VDU.

---

## Direction 4: Learning When Not to Intervene (Clean-State Gating)

- **Research Hypothesis:** Decoupling the "Should I intervene at all?" gate from the "Which intervention is best?" selector achieves higher precision than joint argmax scoring.
- **Algorithm:**
  Two-stage cascaded controller:
  1. Gate: $g(s) = \mathbb{I}[d_{\text{layout}} < \tau_{\text{layout}} \land P_{\text{stop}} \ge \tau_{\text{conf}}]$. If $g(s) = 1$, return $a_{\text{stop}}$ immediately.
  2. Router: If $g(s) = 0$, evaluate $\arg\max_{a \in \text{Active}} V(s, a)$.
- **Closest Prior Work:** Cascade classifiers (Viola-Jones, 2001); Speculative decoding / early exiting (Schuster et al., 2022).
- **Exact Potential Contribution:** Drastically reduces unnecessary intervention compute (Type-I errors) on clean inputs with zero risk of degrading corrupted inputs.
- **Main Failure Mode:** Boundary false positives: gating halts early on subtle corruptions that appear clean globally.
- **Minimum Decisive Experiment:** Measure Unnecessary Intervention Rate (UIR/UCR) on clean subset of 16k benchmark.
- **Data & Compute Requirements:** Existing 16k SQLite records.
- **Falsification Criterion:** If the gate reduces defective-document recovery (RSR) by $>2\%$, hard gating is harmful compared to continuous scoring.

---

## Direction 5: Budgeted Reliability and Selective Prediction (Intervene-Then-Abstain)

- **Research Hypothesis:** Jointly optimizing visual repair, early stopping, and selective abstention under an explicit unsupported-answer penalty creates a superior Accuracy-Coverage-Compute Pareto frontier.
- **Algorithm:**
  $$\max_{\pi} \mathbb{E}\left[ \mathbb{I}[Y=1] - \lambda_{\text{cost}} C - \lambda_{\text{error}} \mathbb{I}[Y=0 \land a \neq \text{abstain}] \right].$$
- **Closest Prior Work:** Selective classification (Geifman & El-Yaniv, 2017); Selective VQA (Kamath et al., 2020).
- **Exact Potential Contribution:** Establishes test-time compute allocation as a mechanism for reducing hallucinations on unanswerable/severely degraded documents.
- **Main Failure Mode:** Excessive abstention on answerable but difficult queries, lowering effective task recall.
- **Minimum Decisive Experiment:** Evaluate selective risk vs coverage curves on the 1,000-sample unanswerable stress test.
- **Data & Compute Requirements:** 1,000 corrupted document records.
- **Falsification Criterion:** If abstention triggers on $>15\%$ of clean, answerable documents, selective tuning fails.

---

## Direction 6: Distribution-Shift-Aware Intervention Selection

- **Research Hypothesis:** Controller performance degrades significantly when transferred to unseen document layouts (e.g., from clean forms to degraded mobile photo receipts); augmenting state telemetry with distribution shift estimators restores robustness.
- **Algorithm:**
  Detect OOD state using Mahalanobis distance on the 16-D telemetry vector: $d_{\text{OOD}}(s) = (f(s) - \mu)^\top \Sigma^{-1} (f(s) - \mu)$. If $d_{\text{OOD}} > \tau$, increase conservatism $\kappa_{\text{OOD}} = \kappa_0 \times (1 + \alpha d_{\text{OOD}})$.
- **Closest Prior Work:** Out-of-distribution detection in RL (Ovadia et al., 2019); Robust Markov Decision Processes (Nilim & El Ghaoui, 2005).
- **Exact Potential Contribution:** First study of test-time compute routing robustness under visual document domain shifts.
- **Main Failure Mode:** Estimating covariance $\Sigma$ on low-dimensional synthetic telemetry features can lead to poorly calibrated distance metrics.
- **Minimum Decisive Experiment:** Train telemetry density on DocVQA/ChartQA, evaluate on TableBench/MMLongBench.
- **Data & Compute Requirements:** Cross-dataset validation splits.
- **Falsification Criterion:** If uniform $\kappa$ achieves equal or better regret than adaptive $\kappa_{\text{OOD}}$, explicit OOD gating is redundant.

---

## Direction 7: Counterfactual Data Efficiency (Adaptive Branching Acquisition)

- **Research Hypothesis:** Rather than branching all $K=4$ candidate interventions across every training instance, an active acquisition policy that only branches on high-uncertainty boundary states reduces counterfactual generation cost by $>60\%$ with $<1\%$ loss in policy accuracy.
- **Algorithm:**
  Prioritize instances for counterfactual branching where $|P_{\text{stop}} - 0.5|$ is maximized or where telemetry variance is high.
- **Closest Prior Work:** Active Learning (Settles, 2009); Efficient Off-Policy Evaluation (Thomas & Brunskill, 2016).
- **Exact Potential Contribution:** Solves the primary scalability criticism of counterfactual data generation (generating branches is expensive).
- **Main Failure Mode:** Boundary-only data induces selection bias in the downstream advantage estimator $f_\psi$.
- **Minimum Decisive Experiment:** Subsample counterfactual training branches using random vs uncertainty sampling; evaluate resulting GVoC router.
- **Data & Compute Requirements:** 160 branches subsampled to 60 branches.
- **Falsification Criterion:** If active subsampling causes $>3\%$ accuracy drop on test scenarios, uniform branching remains necessary.

---

## Direction 8: Statistical Validity of Counterfactual Action Values (Formal Estimator Properties)

- **Research Hypothesis:** The frozen-state branching protocol satisfies the Strong Ignorability condition $(Y(a) \perp A \mid S_t = s_t)$, enabling asymptotically unbiased estimation of counterfactual intervention gains.
- **Algorithm:**
  Formal causal proof showing that since $S_t$ is deterministic and conditioned prior to action dispatch, no unobserved confounding exists.
- **Closest Prior Work:** Neyman-Rubin Causal Model (Rubin, 1974); Causal Inference in ML (Pearl, 2009).
- **Exact Potential Contribution:** Solid theoretical footing that distinguishes GVoC from heuristic RL routers.
- **Main Failure Mode:** Pure theory without empirical engineering contribution may be seen as obvious by statistical reviewers.
- **Minimum Decisive Experiment:** Verification of conditional balance across state features $f(s_t)$.
- **Falsification Criterion:** If state features vary across counterfactual branches prior to intervention execution, ignorability is violated.

---

## Direction 9: Action-Specific Damage vs. Repair Decomposition (Hybrid with Direction 1)

- **Research Hypothesis:** For certain actions (e.g., $a_{\text{reexec}}$), the probability of corrupting an already-correct answer is higher than for pure optical zoom ($a_{\text{reground}}$). Estimating action-specific harm rates $\hat{h}(a)$ allows action-specific conservatism $\kappa_a$.
- **Algorithm:**
  $\mathcal{V}(s, a) = \frac{\max(0, \hat{\Delta P}_a - \kappa_a \hat{\sigma}_a)}{C(a) + \epsilon}$, with $\kappa_{\text{reexec}} > \kappa_{\text{reground}}$.
- **Closest Prior Work:** Cost-sensitive classification (Elkan, 2001); Safe RL (Garcia & Fernandez, 2015).
- **Exact Potential Contribution:** Surgically prevents aggressive table re-parsing while allowing high-resolution zooming.
- **Minimum Decisive Experiment:** Compare uniform $\kappa$ against action-stratified $\kappa_a$.
- **Falsification Criterion:** If $\kappa_{\text{reexec}} = \kappa_{\text{reground}}$ achieves optimal validation regret, action stratification is unneeded.

---

## Direction 10: Conformal Prediction Intervals for Intervention Utility

- **Research Hypothesis:** Using Split Conformal Prediction on held-out paired calibration residuals yields distribution-free finite-sample lower bounds on accuracy improvement $\Delta P_a$.
- **Algorithm:**
  Compute calibration residuals $R_i = \Delta P_i - \hat{\Delta P}_i$ on calibration set. Set $\hat{q}_{1-\alpha}$ as the $(1-\alpha)$ quantile. Conservative score: $\hat{\Delta P}_a - \hat{q}_{1-\alpha}$.
- **Closest Prior Work:** Conformal Prediction (Vovk et al., 2005); Conformal Risk Control (Angelopoulos et al., 2024).
- **Exact Potential Contribution:** Replaces heuristic $\kappa \sigma$ with a formally certified $1 - \alpha$ coverage guarantee.
- **Main Failure Mode:** On small validation sets ($N=20$), conformal quantiles are loose, leading to overly conservative lower bounds ($<0$).
- **Minimum Decisive Experiment:** Calculate empirical coverage and token savings of conformal score vs LCB.
- **Falsification Criterion:** If conformal bound collapses all scores to 0 due to small calibration sample size, the method is infeasible without hundreds of calibration queries.
