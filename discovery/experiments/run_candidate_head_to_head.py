"""
Decisive Head-to-Head Benchmark Execution for the Three Prototype Candidates.

Compares:
1. Monolithic Zero-Shot
2. Fixed VEC-CAP (Deterministic Rule)
3. Confidence-Based Router
4. MACT (Multi-Agent Collaborative Tuning)
5. GVoC (Point-Estimate Baseline)
6. Candidate 1: Risk-Bounded LCB Policy (C-GVoC LCB)
7. Candidate 2: Clean-Gated Policy
8. Candidate 3: Harm-Aware Decomposed Policy
9. Empirical Oracle
"""

import time
import math
import random
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import defaultdict

from gvoc_engine.core.action_space import Action, ActionSpace
from gvoc_engine.core.state import GroundedState
from gvoc_engine.benchmark.fresh_benchmark_loader import get_fresh_benchmark_dataset
from gvoc_engine.pilot.run_pilot import PilotRunner
from gvoc_engine.controllers.gvoc_router import GVoCRouter

from discovery.experiments.candidate_1_risk_bounded.router import RiskBoundedPrototype
from discovery.experiments.candidate_2_clean_gated.router import CleanGatedPrototype
from discovery.experiments.candidate_3_harm_aware.router import HarmAwarePrototype


def bootstrap_ci(data: List[float], n_boot: int = 1000, ci: float = 0.95) -> Tuple[float, float]:
    if not data:
        return 0.0, 0.0
    n = len(data)
    means = []
    for _ in range(n_boot):
        sample = [random.choice(data) for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lower_idx = int((1 - ci) / 2 * n_boot)
    upper_idx = int((1 + ci) / 2 * n_boot)
    return means[lower_idx], means[upper_idx]


def evaluate_all_candidates():
    random.seed(42)
    runner = PilotRunner(use_mock=True)
    dataset = get_fresh_benchmark_dataset()

    # Instantiate routers
    router_gvoc = GVoCRouter(calibration_mode="point_estimate", kappa=0.0)
    router_c1 = RiskBoundedPrototype(kappa=0.10)
    router_c2 = CleanGatedPrototype()
    router_c3 = HarmAwarePrototype(lambda_harm=2.0)

    candidates = [
        "monolithic",
        "fixed_veccap",
        "confidence_router",
        "mact",
        "gvoc_point_estimate",
        "cand_1_risk_bounded",
        "cand_2_clean_gated",
        "cand_3_harm_aware",
        "oracle"
    ]

    records = {c: [] for c in candidates}

    for item in dataset:
        st_dict = item["initial_state"]
        query = item["query"]
        gt = item["ground_truth"]
        eff_set = item["effective_set"]
        domain = item["id"].split("_")[0]
        ftype = item["failure_type"]

        branches = runner.run_counterfactual_branches(st_dict, query, gt, eff_set)
        oracle_best_act, oracle_max_val = runner.oracle_router.select_action_from_oracle(
            {act: b["v_emp"] for act, b in branches.items()}
        )
        st = GroundedState.from_dict(st_dict)

        # Compute mathematically rigorous oracle optimal loss under Eq 2 (lambda=0.85, C_max=500)
        oracle_branch = branches[oracle_best_act]
        oracle_loss = 0.85 * (1 - oracle_branch["is_correct"]) + 0.15 * (oracle_branch["tokens"] / 500.0)

        for c in candidates:
            t0 = time.perf_counter()
            if c == "monolithic":
                chosen = runner.monolithic.select_action(st, 2000)
            elif c == "fixed_veccap":
                chosen = runner.fixed_veccap.select_action(st, 2000)
            elif c == "confidence_router":
                chosen = runner.confidence_router.select_action(st, 2000)
            elif c == "mact":
                chosen = runner.mact.select_action(st, 2000)
            elif c == "gvoc_point_estimate":
                chosen, _ = router_gvoc.select_action(st, 2000)
            elif c == "cand_1_risk_bounded":
                chosen, _ = router_c1.select_action(st, 2000)
            elif c == "cand_2_clean_gated":
                chosen, _ = router_c2.select_action(st, 2000)
            elif c == "cand_3_harm_aware":
                chosen, _ = router_c3.select_action(st, 2000)
            elif c == "oracle":
                chosen = oracle_best_act
            else:
                chosen = Action.STOP
            lat_ms = (time.perf_counter() - t0) * 1000

            b_res = branches[chosen]
            y_stop = branches[Action.STOP]["is_correct"]
            y_final = b_res["is_correct"]
            tokens_total = 250 + b_res["tokens"]

            # Mathematical Normalized Regret strictly in [0, 1]
            cand_loss = 0.85 * (1 - y_final) + 0.15 * (b_res["tokens"] / 500.0)
            regret_norm = max(0.0, cand_loss - oracle_loss)

            # Harm rate: broke a previously correct answer
            is_harm = 1 if y_stop == 1 and y_final == 0 and ActionSpace.is_active(chosen) else 0

            # Clean document Type-I error (fired on normal_correct_state)
            is_type1 = 1 if ftype == "normal_correct_state" and ActionSpace.is_active(chosen) else 0

            records[c].append({
                "id": item["id"],
                "domain": domain,
                "is_val": domain in ["docvqa", "chartqa"],
                "ftype": ftype,
                "chosen_action": chosen.value,
                "is_correct": y_final,
                "tokens": tokens_total,
                "regret_norm": regret_norm,
                "is_harm": is_harm,
                "is_type1": is_type1,
                "lat_ms": lat_ms
            })

    # Summary table
    print("\n" + "=" * 115)
    print(" HEAD-TO-HEAD DECISIVE BENCHMARK EVALUATION (N = 40 PAIRED SCENARIOS)")
    print("=" * 115)
    print(f"{'Method / Candidate':<24} | {'Acc (%) [95% CI]':<20} | {'Tokens':<8} | {'Regret [0,1]':<12} | {'Harm %':<8} | {'Type-I %':<8} | {'Lat (ms)':<8}")
    print("-" * 115)

    summary_stats = {}
    for c in candidates:
        recs = records[c]
        n = len(recs)
        acc_vals = [r["is_correct"] * 100 for r in recs]
        mean_acc = sum(acc_vals) / n
        ci_acc = bootstrap_ci(acc_vals)

        tok_vals = [r["tokens"] for r in recs]
        mean_tok = sum(tok_vals) / n

        reg_vals = [r["regret_norm"] for r in recs]
        mean_reg = sum(reg_vals) / n
        ci_reg = bootstrap_ci(reg_vals)

        harm_rate = sum(r["is_harm"] for r in recs) / n * 100
        type1_rate = sum(r["is_type1"] for r in recs) / sum(1 for r in recs if r["ftype"] == "normal_correct_state") * 100
        mean_lat = sum(r["lat_ms"] for r in recs) / n

        summary_stats[c] = {
            "mean_acc": mean_acc,
            "ci_acc": ci_acc,
            "mean_tok": mean_tok,
            "mean_reg": mean_reg,
            "ci_reg": ci_reg,
            "harm_rate": harm_rate,
            "type1_rate": type1_rate,
            "mean_lat": mean_lat
        }

        print(f"{c:<24} | {mean_acc:>5.1f}% [{ci_acc[0]:>4.1f},{ci_acc[1]:>4.1f}] | {mean_tok:>8.1f} | {mean_reg:>6.4f} [{ci_reg[0]:.3f},{ci_reg[1]:.3f}] | {harm_rate:>6.1f}% | {type1_rate:>6.1f}% | {mean_lat:>7.3f}")
    print("=" * 115)

    # Stratified: Validation (DocVQA, ChartQA) vs Held-Out Test (TableBench, MMLongBench)
    print("\n" + "=" * 115)
    print(" STRATIFIED EVALUATION: VALIDATION (N=20) VS HELD-OUT TEST (N=20)")
    print("=" * 115)
    print(f"{'Method / Candidate':<24} | {'Val Acc (%)':<12} | {'Val Tok':<8} | {'Val Reg':<10} | {'Test Acc (%)':<12} | {'Test Tok':<8} | {'Test Reg':<10}")
    print("-" * 115)

    for c in candidates:
        val_recs = [r for r in records[c] if r["is_val"]]
        test_recs = [r for r in records[c] if not r["is_val"]]

        v_acc = sum(r["is_correct"] for r in val_recs) / len(val_recs) * 100
        v_tok = sum(r["tokens"] for r in val_recs) / len(val_recs)
        v_reg = sum(r["regret_norm"] for r in val_recs) / len(val_recs)

        t_acc = sum(r["is_correct"] for r in test_recs) / len(test_recs) * 100
        t_tok = sum(r["tokens"] for r in test_recs) / len(test_recs)
        t_reg = sum(r["regret_norm"] for r in test_recs) / len(test_recs)

        print(f"{c:<24} | {v_acc:>10.1f}% | {v_tok:>8.1f} | {v_reg:>8.4f} | {t_acc:>10.1f}% | {t_tok:>8.1f} | {t_reg:>8.4f}")
    print("=" * 115)

    # Save results to json
    results_path = Path("discovery/experiments/benchmark_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(summary_stats, f, indent=2)
    print(f"\n[Saved benchmark results to {results_path}]")


if __name__ == "__main__":
    evaluate_all_candidates()
