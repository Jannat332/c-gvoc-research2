"""
Dedicated Live Empirical Pilot Runner for GVoC / C-GVoC Validation.
Runs 100 preregistered genuine multimodal document/chart instances.
Logs all API calls and counterfactual episodes into discovery/live_validation/live_evaluation.db.
RESEARCH INTEGRITY: Mock fallback is STRICTLY DISABLED.
"""

import os
import sys
import json
import time
import uuid
import datetime
import sqlite3
from pathlib import Path
from typing import Dict, Any, List

from discovery.live_validation.live_client import LiveVLMClient, LiveAPIError
from discovery.live_validation.live_db import init_live_db, log_call, log_episode, DB_PATH
from discovery.live_validation.scoring import score_vdu_answer, normalize_text
from gvoc_engine.core.state import build_grounded_state_vector
from gvoc_engine.controllers.gvoc_router import GVoCRouter
from gvoc_engine.core.action_space import GVoCAction


def init_diagnostic_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS live_counterfactual_actions (
        id TEXT PRIMARY KEY,
        experiment_id TEXT NOT NULL,
        instance_id TEXT NOT NULL,
        dataset TEXT NOT NULL,
        action TEXT NOT NULL,
        predicted_delta REAL NOT NULL,
        true_delta REAL NOT NULL,
        prediction_error REAL NOT NULL,
        sigma_proxy REAL NOT NULL,
        c_exec REAL NOT NULL,
        d_layout REAL NOT NULL,
        d_evidence REAL NOT NULL,
        tokens_spent INTEGER NOT NULL,
        is_beneficial INTEGER NOT NULL
    )
    """)
    conn.commit()
    conn.close()


def log_counterfactual(row: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO live_counterfactual_actions (
        id, experiment_id, instance_id, dataset, action, predicted_delta,
        true_delta, prediction_error, sigma_proxy, c_exec, d_layout,
        d_evidence, tokens_spent, is_beneficial
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["id"], row["experiment_id"], row["instance_id"], row["dataset"],
        row["action"], row["predicted_delta"], row["true_delta"],
        row["prediction_error"], row["sigma_proxy"], row["c_exec"],
        row["d_layout"], row["d_evidence"], row["tokens_spent"],
        row["is_beneficial"]
    ))
    conn.commit()
    conn.close()


def run_live_pilot(max_instances: int = 100):
    print("\n" + "=" * 80)
    print("STARTING LIVE EMPIRICAL PILOT: 100 FROZEN MULTIMODAL VDU INSTANCES")
    print("Model: Mistral Pixtral-12B (pixtral-12b-2409) | Provider: Mistral AI")
    print("Database: discovery/live_validation/live_evaluation.db")
    print("Integrity: Mock fallback strictly disabled; all calls verified live.")
    print("=" * 80 + "\n")

    init_live_db()
    init_diagnostic_table()

    client = LiveVLMClient("mistral")
    gvoc_router = GVoCRouter()

    instances_file = Path("discovery/live_validation/pilot_dataset/preregistered_100.json")
    with open(instances_file, "r", encoding="utf-8") as f:
        instances = json.load(f)[:max_instances]

    exp_id = f"live_pilot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    t_start = time.time()

    successful_instances = 0
    failed_instances = 0

    for idx, inst in enumerate(instances):
        inst_id = inst["instance_id"]
        dataset = inst["dataset"]
        q = inst["query"]
        img_path = inst["image_path"]
        gt = inst["ground_truth"]

        print(f"\n--- [{idx+1}/{len(instances)}] Instance: {inst_id} ({dataset.upper()}) ---")
        print(f"Query: {q}")
        print(f"GT: {gt[:2]}")

        try:
            # 1. Monolithic Direct Call (Stop branch)
            p_init = f"Answer the question directly and concisely based on the visual document or chart.\nQuestion: {q}\nAnswer:"
            res_init = client.call(p_init, image_path=img_path, max_tokens=60)
            ans_init = res_init["text"]
            f1_init, corr_init = score_vdu_answer(ans_init, gt)

            call_id_init = f"{exp_id}_{inst_id}_init"
            log_call({
                "call_id": call_id_init,
                "experiment_id": exp_id,
                "instance_id": inst_id,
                "method": "monolithic",
                "call_role": "initial_inference",
                "dataset": dataset,
                "split": inst["source_split"],
                "provider": res_init["provider"],
                "model_id": res_init["model_id"],
                "timestamp": datetime.datetime.now().isoformat(),
                "latency_sec": res_init["latency_sec"],
                "status": res_init["status"],
                "attempt": res_init["attempt"],
                "prompt_text": p_init,
                "image_path": img_path,
                "response_text": ans_init,
                "prompt_tokens": res_init["prompt_tokens"],
                "completion_tokens": res_init["completion_tokens"],
                "total_tokens": res_init["total_tokens"],
                "est_cost_usd": (res_init["total_tokens"] / 1000) * 0.00015
            })

            time.sleep(0.2)

            # 2. Re-grounding Intervention Call
            p_reground = f"Examine the document/chart carefully with high precision around the relevant visual area to answer accurately.\nQuestion: {q}\nAnswer:"
            res_rg = client.call(p_reground, image_path=img_path, max_tokens=60)
            ans_rg = res_rg["text"]
            f1_rg, corr_rg = score_vdu_answer(ans_rg, gt)

            call_id_rg = f"{exp_id}_{inst_id}_reground"
            log_call({
                "call_id": call_id_rg,
                "experiment_id": exp_id,
                "instance_id": inst_id,
                "method": "intervention",
                "call_role": "reground",
                "dataset": dataset,
                "split": inst["source_split"],
                "provider": res_rg["provider"],
                "model_id": res_rg["model_id"],
                "timestamp": datetime.datetime.now().isoformat(),
                "latency_sec": res_rg["latency_sec"],
                "status": res_rg["status"],
                "attempt": res_rg["attempt"],
                "prompt_text": p_reground,
                "image_path": img_path,
                "response_text": ans_rg,
                "prompt_tokens": res_rg["prompt_tokens"],
                "completion_tokens": res_rg["completion_tokens"],
                "total_tokens": res_rg["total_tokens"],
                "est_cost_usd": (res_rg["total_tokens"] / 1000) * 0.00015
            })

            time.sleep(0.2)

            # 3. Re-execute / Verification Intervention Call
            p_reexec = f"Carefully verify the values and step-by-step logic from the visual document to answer the question:\nQuestion: {q}\nState the final concise answer on the last line after 'Final Answer:'"
            res_rx = client.call(p_reexec, image_path=img_path, max_tokens=80)
            raw_rx = res_rx["text"]
            ans_rx = raw_rx.split("Final Answer:")[-1].strip() if "Final Answer:" in raw_rx else raw_rx
            f1_rx, corr_rx = score_vdu_answer(ans_rx, gt)

            call_id_rx = f"{exp_id}_{inst_id}_reexec"
            log_call({
                "call_id": call_id_rx,
                "experiment_id": exp_id,
                "instance_id": inst_id,
                "method": "intervention",
                "call_role": "reexec",
                "dataset": dataset,
                "split": inst["source_split"],
                "provider": res_rx["provider"],
                "model_id": res_rx["model_id"],
                "timestamp": datetime.datetime.now().isoformat(),
                "latency_sec": res_rx["latency_sec"],
                "status": res_rx["status"],
                "attempt": res_rx["attempt"],
                "prompt_text": p_reexec,
                "image_path": img_path,
                "response_text": raw_rx,
                "prompt_tokens": res_rx["prompt_tokens"],
                "completion_tokens": res_rx["completion_tokens"],
                "total_tokens": res_rx["total_tokens"],
                "est_cost_usd": (res_rx["total_tokens"] / 1000) * 0.00015
            })

            # Derive telemetry features and uncertainty proxy
            # Confidence proxy based on output structure and lexical certainty
            hedging_words = ["maybe", "might", "approx", "unclear", "not visible", "possibly", "cannot determine"]
            has_hedge = any(h in ans_init.lower() for h in hedging_words)
            c_exec = 0.40 if has_hedge else (0.85 if len(ans_init.split()) <= 6 else 0.65)
            d_layout = 0.45 if dataset == "docvqa" else 0.25
            d_evidence = 0.50 if has_hedge else 0.20
            c_consensus = max(0.05, c_exec - 0.5 * (d_layout + d_evidence))

            # Grounded state vector
            s_t = build_grounded_state_vector(
                C_plan=0.75,
                C_exec=c_exec,
                C_judg=0.70,
                C_consensus=c_consensus,
                D_layout=d_layout,
                D_traj=0.10,
                D_evidence=d_evidence,
                D_answer=0.15,
                rho_visual=0.65,
                B_t=1.0,
                N_tokens=res_init["total_tokens"]
            )

            # Telemetry dispersion uncertainty proxy:
            # sigma_a(s) = sqrt((1 - C_consensus)^2 + D_layout^2 + D_evidence^2)
            sigma_proxy = float(((1.0 - c_consensus)**2 + d_layout**2 + d_evidence**2)**0.5)

            # Evaluate Policy Routing Decisions
            # 1. Monolithic (Stop-only)
            log_episode({
                "episode_id": f"{exp_id}_{inst_id}_mono",
                "experiment_id": exp_id,
                "instance_id": inst_id,
                "method": "monolithic",
                "dataset": dataset,
                "model_id": res_init["model_id"],
                "chosen_action": "stop",
                "final_answer": ans_init,
                "is_correct": corr_init,
                "is_abstain": 0,
                "tokens_spent": res_init["total_tokens"],
                "latency_sec": res_init["latency_sec"],
                "est_cost_usd": (res_init["total_tokens"] / 1000) * 0.00015,
                "raw_telemetry": {"c_exec": c_exec, "sigma_proxy": sigma_proxy},
                "ground_truth": gt,
                "query": q
            })

            # 2. Deterministic Router (triggers reground if c_exec < 0.70)
            det_action = "reground" if c_exec < 0.70 else "stop"
            det_ans = ans_rg if det_action == "reground" else ans_init
            det_corr = corr_rg if det_action == "reground" else corr_init
            det_tokens = res_init["total_tokens"] + (res_rg["total_tokens"] if det_action == "reground" else 0)
            det_lat = res_init["latency_sec"] + (res_rg["latency_sec"] if det_action == "reground" else 0)
            log_episode({
                "episode_id": f"{exp_id}_{inst_id}_det",
                "experiment_id": exp_id,
                "instance_id": inst_id,
                "method": "deterministic",
                "dataset": dataset,
                "model_id": res_init["model_id"],
                "chosen_action": det_action,
                "final_answer": det_ans,
                "is_correct": det_corr,
                "is_abstain": 0,
                "tokens_spent": det_tokens,
                "latency_sec": det_lat,
                "est_cost_usd": (det_tokens / 1000) * 0.00015,
                "raw_telemetry": {"c_exec": c_exec, "sigma_proxy": sigma_proxy},
                "ground_truth": gt,
                "query": q
            })

            # 3. Original GVoC (lambda = 0.0)
            # Evaluate advantage of reground and reexec
            gvoc_act, gvoc_meta = gvoc_router.select_action(s_t, remaining_budget=2000)
            act_name = gvoc_act.value if hasattr(gvoc_act, "value") else str(gvoc_act)
            if act_name == "reground":
                gvoc_ans, gvoc_corr, gvoc_tok = ans_rg, corr_rg, res_init["total_tokens"] + res_rg["total_tokens"]
            elif act_name in ["replan", "reexecute"]:
                gvoc_ans, gvoc_corr, gvoc_tok = ans_rx, corr_rx, res_init["total_tokens"] + res_rx["total_tokens"]
            elif act_name == "abstain":
                gvoc_ans, gvoc_corr, gvoc_tok = "[ABSTAIN]", 0, res_init["total_tokens"]
            else:
                gvoc_ans, gvoc_corr, gvoc_tok = ans_init, corr_init, res_init["total_tokens"]

            log_episode({
                "episode_id": f"{exp_id}_{inst_id}_gvoc",
                "experiment_id": exp_id,
                "instance_id": inst_id,
                "method": "gvoc",
                "dataset": dataset,
                "model_id": res_init["model_id"],
                "chosen_action": act_name,
                "final_answer": gvoc_ans,
                "is_correct": gvoc_corr,
                "is_abstain": 1 if act_name == "abstain" else 0,
                "tokens_spent": gvoc_tok,
                "latency_sec": res_init["latency_sec"],
                "est_cost_usd": (gvoc_tok / 1000) * 0.00015,
                "raw_telemetry": {"c_exec": c_exec, "sigma_proxy": sigma_proxy},
                "ground_truth": gt,
                "query": q
            })

            # 4. C-GVoC (lambda = 0.5 conservative penalty)
            # Penalizes intervention score: (delta_a - lambda * sigma_proxy) / Cost
            # If net score <= 0, falls back to STOP
            cgvoc_scores = {}
            for cand_act, score_key in [("reground", "reground"), ("reexecute", "reexec")]:
                # Estimated advantage from router scores
                base_delta = gvoc_meta.get("scores", {}).get(score_key, {}).get("delta_p", 0.40)
                cost_norm = 1.2 if cand_act == "reground" else 1.5
                penalized_gain = base_delta - 0.5 * sigma_proxy
                cgvoc_scores[cand_act] = penalized_gain / cost_norm

            best_cand = max(cgvoc_scores, key=cgvoc_scores.get)
            if cgvoc_scores[best_cand] > 0.05:
                cgvoc_act = best_cand
            else:
                cgvoc_act = "stop"

            if cgvoc_act == "reground":
                cgvoc_ans, cgvoc_corr, cgvoc_tok = ans_rg, corr_rg, res_init["total_tokens"] + res_rg["total_tokens"]
            elif cgvoc_act == "reexecute":
                cgvoc_ans, cgvoc_corr, cgvoc_tok = ans_rx, corr_rx, res_init["total_tokens"] + res_rx["total_tokens"]
            else:
                cgvoc_act = "stop"
                cgvoc_ans, cgvoc_corr, cgvoc_tok = ans_init, corr_init, res_init["total_tokens"]

            log_episode({
                "episode_id": f"{exp_id}_{inst_id}_cgvoc",
                "experiment_id": exp_id,
                "instance_id": inst_id,
                "method": "cgvoc",
                "dataset": dataset,
                "model_id": res_init["model_id"],
                "chosen_action": cgvoc_act,
                "final_answer": cgvoc_ans,
                "is_correct": cgvoc_corr,
                "is_abstain": 0,
                "tokens_spent": cgvoc_tok,
                "latency_sec": res_init["latency_sec"],
                "est_cost_usd": (cgvoc_tok / 1000) * 0.00015,
                "raw_telemetry": {"c_exec": c_exec, "sigma_proxy": sigma_proxy, "lambda": 0.5},
                "ground_truth": gt,
                "query": q
            })

            # 5. Offline Counterfactual Oracle (Diagnostic Bound)
            cand_results = [
                ("stop", corr_init, res_init["total_tokens"], ans_init),
                ("reground", corr_rg, res_init["total_tokens"] + res_rg["total_tokens"], ans_rg),
                ("reexecute", corr_rx, res_init["total_tokens"] + res_rx["total_tokens"], ans_rx)
            ]
            # Maximize accuracy - tiny token penalty
            best_oracle = max(cand_results, key=lambda x: (x[1], -x[2]))
            oracle_act, oracle_corr, oracle_tok, oracle_ans = best_oracle
            log_episode({
                "episode_id": f"{exp_id}_{inst_id}_oracle",
                "experiment_id": exp_id,
                "instance_id": inst_id,
                "method": "oracle",
                "dataset": dataset,
                "model_id": res_init["model_id"],
                "chosen_action": oracle_act,
                "final_answer": oracle_ans,
                "is_correct": oracle_corr,
                "is_abstain": 0,
                "tokens_spent": oracle_tok,
                "latency_sec": res_init["latency_sec"],
                "est_cost_usd": (oracle_tok / 1000) * 0.00015,
                "raw_telemetry": {"oracle_diagnostic": True},
                "ground_truth": gt,
                "query": q
            })

            # Log Counterfactual Diagnostics for Phase 4 uncertainty validation
            # For REGROUND:
            true_delta_rg = float(corr_rg - corr_init)
            pred_delta_rg = gvoc_meta.get("scores", {}).get("reground", {}).get("delta_p", 0.40)
            err_rg = abs(pred_delta_rg - true_delta_rg)
            log_counterfactual({
                "id": f"{exp_id}_{inst_id}_rg",
                "experiment_id": exp_id,
                "instance_id": inst_id,
                "dataset": dataset,
                "action": "reground",
                "predicted_delta": pred_delta_rg,
                "true_delta": true_delta_rg,
                "prediction_error": err_rg,
                "sigma_proxy": sigma_proxy,
                "c_exec": c_exec,
                "d_layout": d_layout,
                "d_evidence": d_evidence,
                "tokens_spent": res_rg["total_tokens"],
                "is_beneficial": 1 if true_delta_rg > 0 else 0
            })

            # For REEXEC:
            true_delta_rx = float(corr_rx - corr_init)
            pred_delta_rx = gvoc_meta.get("scores", {}).get("reexec", {}).get("delta_p", 0.35)
            err_rx = abs(pred_delta_rx - true_delta_rx)
            log_counterfactual({
                "id": f"{exp_id}_{inst_id}_rx",
                "experiment_id": exp_id,
                "instance_id": inst_id,
                "dataset": dataset,
                "action": "reexecute",
                "predicted_delta": pred_delta_rx,
                "true_delta": true_delta_rx,
                "prediction_error": err_rx,
                "sigma_proxy": sigma_proxy,
                "c_exec": c_exec,
                "d_layout": d_layout,
                "d_evidence": d_evidence,
                "tokens_spent": res_rx["total_tokens"],
                "is_beneficial": 1 if true_delta_rx > 0 else 0
            })

            successful_instances += 1
            print(f"  Outcomes: Mono={corr_init} | Reground={corr_rg} | Reexec={corr_rx} | Oracle={oracle_act} | C-GVoC Choice={cgvoc_act}")

        except Exception as e:
            failed_instances += 1
            print(f"  [ERROR] Instance {inst_id} failed: {type(e).__name__}: {e}")

        time.sleep(0.3)

    dt_total = time.time() - t_start
    print("\n" + "=" * 80)
    print(f"PILOT EXECUTION COMPLETE in {dt_total:.1f}s")
    print(f"Successful instances: {successful_instances} | Failed instances: {failed_instances}")
    print("Database committed to discovery/live_validation/live_evaluation.db")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_live_pilot(100)
