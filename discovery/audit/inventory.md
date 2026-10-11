# Inventory and Codebase Audit

**Date:** 2026-10-10  
**Repository:** `c:/Users/user/Desktop/recent_projects/ESWA_ehte`  
**Git Branch:** `naacl_master_loop_audit`  
**Git Commit:** `2f92f78` (Latest commit: *"Implement and evaluate Risk-Bounded Counterfactual Intervention Policy with paired-outcome uncertainty estimation and held-out validation tuning"*)  
**Python Environment:** Python 3.13.0 (Windows x64)

---

## 1. Project Overview & Architecture

The project investigates test-time compute allocation for Visual Document Understanding (VDU), contrasting **reasoning-space scaling** (e.g., chain-of-thought, multi-agent debate) with **observation-space scaling** (e.g., localized high-resolution optical cropping, table schema re-execution, safe abstention).

The manuscript target is NAACL (Short Paper format, strictly 4 pages main text, plus references and appendices).

### Primary Modules in `gvoc_engine/`

1. **Core Abstractions (`gvoc_engine/core/`):**
   - `action_space.py`: Defines `Action` enum (`STOP`, `REGROUND`, `REPLAN`, `REEXEC`, `VERIFY`, `ABSTAIN`) and helper predicates (`is_active`, `is_terminal`). Also defines `GVoCAction` (`stop`, `reground`, `reexecute`, `abstain`).
   - `state.py`: Defines `GroundedState` (dataclass containing 10 intermediate diagnostic signals: `c_plan`, `c_exec`, `c_judg`, `c_consensus`, `d_layout`, `d_traj`, `d_evidence`, `d_answer`, `rho_visual`, `current_bbox`, etc.) and `build_grounded_state_vector`.
   - `database.py`: Manages SQLite storage in `gvoc_evaluation.db` (`task_evaluations` table for instance-level runs, `intervention_steps` for step-level decisions).
   - `status_updater.py`: Updates real-time terminal progress.

2. **Decision Controllers (`gvoc_engine/controllers/`):**
   - `gvoc_router.py`: Implements `GVoCRouter`. Evaluates intervention advantage $\Delta P_a(s)$ and cost $C(s, a)$. Computes ratio $V(s, a) = \Delta P_a / (C_a + \epsilon)$. Supports `calibration_mode="point_estimate"` and `calibration_mode="conservative"`.
   - `risk_bounded_router.py`: Implements `RiskBoundedCounterfactualRouter`. Uses a Lower Confidence Bound (LCB) on accuracy improvement: $\mathcal{V}_{\text{LCB}}(s, a) = \frac{\max(0, \hat{\Delta P}_a(s) - \kappa \hat{\sigma}_a(s))}{C(s, a) + \epsilon}$. Distinguishes action uncertainty from evidence insufficiency.
   - `baselines.py`: Implements baseline policies:
     - `MonolithicBaseline`: Always emits `STOP` on initial low-resolution pass.
     - `SelfConsistencyBaseline`: Multiple stochastic passes without tool intervention.
     - `FixedVECCAPBaseline`: Deterministic heuristic threshold rules on layout and confidence.
     - `MACTBaseline`: Agent-level re-allocation (planning/execution retries).
     - `ConfidenceRouterBaseline`: Semantic confidence threshold router.
     - `OracleGVoCRouter`: Empirical upper bound selecting $\arg\max_a V_{\text{emp}}(s, a)$.
     - Standalone evaluators: `evaluate_monolithic`, `evaluate_fixed_veccap`, `evaluate_mact`, `evaluate_confidence_router`, `evaluate_empirical_oracle`.

3. **Benchmark & Datasets (`gvoc_engine/benchmark/` & `gvoc_engine/data/`):**
   - `fresh_benchmark_loader.py`: 40 detailed diagnostic scenarios with verified paired states across 4 datasets (DocVQA, ChartQA, TableBench, MMLongBench-Doc).
   - `perturbations.py`: Multi-severity failure perturbation engine (spatial shifts, reading order inversion, OCR character noise, arithmetic swap).
   - `effective_sets.py`: Ground-truth mapping from failure mode to Effective Intervention Set $\mathcal{A}^*$.
   - Data files (`gvoc_engine/data/`):
     - `docvqa_1k.jsonl`: 1,000 synthetic/cached problem instances.
     - `chartqa_1k.jsonl`: 1,000 synthetic/cached problem instances.
     - `tablebench_1k.jsonl`: 1,000 synthetic/cached problem instances.
     - `mmlongbench_1k.jsonl`: 1,000 synthetic/cached problem instances.

4. **Pilot & Evaluation Harness (`gvoc_engine/pilot/` & `gvoc_engine/experiments/`):**
   - `run_pilot.py`: `PilotRunner` orchestrates counterfactual branching from frozen intermediate states $s_t$, evaluating all actions under identical base state.
   - `run_full_16k_benchmark.py`: Runs simulation across 4 models $\times$ 4 datasets $\times$ 1,000 instances = 16,000 episodes for 6 baselines (96,000 evaluations total). Commits to SQLite `task_evaluations`.
   - `run_risk_bounded_evaluation.py`: Full evaluation of Risk-Bounded Router vs Point Estimate vs Baselines on the 40 paired scenarios with bootstrap 95% CIs.
   - `run_cgvoc_head_to_head.py`: Comparative ablation harness for C-GVoC vs GVoC.
   - `gvoc_evaluation.db`: SQLite database storing 16,137 logged GVoC evaluations and baseline comparison runs.

5. **Unit Tests (`gvoc_engine/tests/`):**
   - `test_cgvoc.py`: 6 tests verifying $\kappa=0$ equivalence, monotonicity, clean-state suppression, safe abstention, budget exhaustion.
   - `test_risk_bounded_router.py`: 6 tests verifying paired alignment, uncertainty dynamics, negative benefit clipping, terminal action handling, budget limits.

6. **Manuscript Source (`naacl/`):**
   - `main.tex`: LaTeX source, compiled cleanly to 12 pages total (strictly 4 pages main text, pages 5-6 references, pages 7-12 appendices).
   - `custom.bib`: Bibliography file with 36 curated, verified references.
   - `main.pdf`: Compiled PDF output.

---

## 2. Dependencies & Build Status

- **LaTeX Engine:** MiKTeX `pdflatex` (compiles `main.tex` with exit code 0).
- **Python Dependencies:** `pytest`, `sqlite3`, `pathlib`, `json`, `math`, `time`.
- **Test Suite Status:** 12 of 12 unit tests currently pass via `python -m pytest -v` in 0.10s.
