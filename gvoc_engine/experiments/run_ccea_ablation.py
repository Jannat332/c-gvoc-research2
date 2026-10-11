"""
Experimental Evaluation and Central Ablation:
Context-Preserving, Cost-Aware Visual Evidence Acquisition (CCEA).

Ablation comparison across 4 conditions:
1. Full_Overview: Monolithic inference on full image.
2. Target_Only_Crop: Tight crop around target evidence (dropping context).
3. CCEA_Context_Preserving: Crop covering target + required headers, labels, and units.
4. CCEA_Cost_Aware_Controller: Adaptive decision policy balancing expected gain vs compute cost.
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image

from discovery.live_validation.scoring import score_vdu_answer
from gvoc_engine.core.state import GroundedState
from gvoc_engine.core.action_space import Action
from gvoc_engine.interventions.context_preservation import (
    Box,
    ContextKind,
    EvidenceRegion,
    assess_crop,
    propose_context_preserving_crop,
    expand_box,
    validate_box,
)
from gvoc_engine.interventions.ccea_intervention import CCEAIntervention, CCEAResult
from gvoc_engine.controllers.ccea_router import CCEACostAwareRouter


class MockAblationClient:
    """Deterministic client for offline testing and plumbing validation."""
    def __init__(self):
        self.calls = 0

    def call_vlm(self, prompt: str, image_path: str, max_tokens: int = 100):
        self.calls += 1
        p_tok, c_tok, lat = 120, 25, 0.08
        if "Localization" in prompt:
            return "[400, 200, 550, 450]", p_tok, c_tok, lat
        if "without any headers or labels" in prompt or "Target_Only" in prompt:
            # Missing context leads to ambiguous or hallucinated answer
            return "42.0", p_tok, c_tok, lat
        return "1128 SIXTEENTH ST., N. W., WASHINGTON, D. C. 20036", p_tok, c_tok, lat


def load_curated_eval_instances(limit: int = 10) -> List[Dict[str, Any]]:
    """Loads genuine document instances from discovery/live_validation/pilot_dataset/instances.json."""
    instances_path = Path("discovery/live_validation/pilot_dataset/instances.json")
    if not instances_path.exists():
        raise FileNotFoundError(f"Dataset not found at {instances_path}")
    
    with open(instances_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Filter instances that have existing local image files
    valid_items = []
    for item in data:
        img_p = Path(item["image_path"])
        if img_p.exists():
            valid_items.append(item)
        if len(valid_items) >= limit:
            break
    return valid_items


def create_synthetic_evidence_region(width: int, height: int, inst_id: str) -> EvidenceRegion:
    """Constructs documented target region and required semantic context boxes for ablation testing."""
    # Target value cell in document body
    t_y0, t_x0 = int(0.40 * height), int(0.35 * width)
    t_y1, t_x1 = int(0.48 * height), int(0.55 * width)
    target_box = (t_y0, t_x0, t_y1, t_x1)

    # Required semantic context regions needed to interpret the cell correctly
    col_header = (int(0.20 * height), int(0.35 * width), int(0.28 * height), int(0.55 * width))
    row_label  = (int(0.40 * height), int(0.10 * width), int(0.48 * height), int(0.32 * width))
    unit_box   = (int(0.12 * height), int(0.10 * width), int(0.18 * height), int(0.30 * width))
    footnote   = (int(0.85 * height), int(0.10 * width), int(0.92 * height), int(0.60 * width))

    return EvidenceRegion(
        target_box=target_box,
        required_context=(
            (ContextKind.COLUMN_LABEL, col_header),
            (ContextKind.ROW_LABEL, row_label),
            (ContextKind.UNIT, unit_box),
            (ContextKind.FOOTNOTE, footnote),
        ),
        evidence_id=f"evidence_{inst_id}"
    )


def run_ccea_ablation(num_samples: int = 10, use_live: bool = False):
    print("=" * 80)
    print("RUNNING CENTRAL ABLATION: CONTEXT-PRESERVING VS. UNCONSTRAINED ACQUISITION")
    print(f"Sample size: {num_samples} | Mode: {'LIVE API' if use_live else 'OFFLINE MOCK / PIPELINE VALIDATION'}")
    print("=" * 80 + "\n")

    instances = load_curated_eval_instances(limit=num_samples)
    print(f"Loaded {len(instances)} instances with valid image assets.\n")

    if use_live:
        from discovery.live_validation.live_client import LiveVLMClient
        client = LiveVLMClient("mistral")
    else:
        client = MockAblationClient()

    intervention = CCEAIntervention(output_dir="discovery/live_validation/confirmatory_experiment/transformed_images")
    router = CCEACostAwareRouter(kappa=0.40, lambda_cost=0.25, tau_safe=0.45, tau_clean=0.75)

    conditions = [
        "1_full_overview",
        "2_target_only_crop",
        "3_ccea_context_preserving",
        "4_ccea_cost_aware_controller"
    ]

    stats = {
        cond: {
            "correct_count": 0,
            "total_f1": 0.0,
            "total_tokens": 0,
            "total_latency": 0.0,
            "context_retained_count": 0,
            "context_lost_count": 0,
            "lost_by_kind": {k.value: 0 for k in ContextKind},
        }
        for cond in conditions
    }

    controller_decisions = {"stop": 0, "acquire": 0, "abstain": 0}
    all_records = []

    for idx, inst in enumerate(instances):
        inst_id = inst["instance_id"]
        q = inst["query"]
        gt = inst["ground_truth"]
        img_path = inst["image_path"]

        with Image.open(img_path) as img:
            w, h = img.size

        evidence = create_synthetic_evidence_region(w, h, inst_id)

        print(f"[{idx+1}/{len(instances)}] Instance {inst_id} ({w}x{h}): {q[:55]}...")

        # -------------------------------------------------------------
        # Condition 1: Full_Overview (No crop)
        # -------------------------------------------------------------
        p_full = f"Answer concisely based on the visual document:\nQuestion: {q}\nAnswer:"
        t0 = time.time()
        if hasattr(client, "call_vlm"):
            ans_full, p_tok, c_tok, lat = client.call_vlm(p_full, img_path, max_tokens=60)
        else:
            res_dict = client.call(p_full, image_path=img_path, max_tokens=60)
            ans_full, p_tok, c_tok, lat = res_dict.get("text", ""), res_dict.get("prompt_tokens", 0), res_dict.get("completion_tokens", 0), res_dict.get("latency_sec", 0.0)

        f1_full, acc_full = score_vdu_answer(ans_full, gt)
        stats["1_full_overview"]["correct_count"] += acc_full
        stats["1_full_overview"]["total_f1"] += f1_full
        stats["1_full_overview"]["total_tokens"] += (p_tok + c_tok)
        stats["1_full_overview"]["total_latency"] += lat
        # Full image has all context visible by definition
        stats["1_full_overview"]["context_retained_count"] += 1

        # -------------------------------------------------------------
        # Condition 2: Target_Only_Crop (Ablation without context preservation)
        # -------------------------------------------------------------
        res_target_only = intervention.execute(
            image_path=img_path,
            query=q,
            client=client,
            evidence_region=evidence,
            initial_answer=ans_full,
            preserve_context=False  # Target crop only!
        )
        f1_tgt, acc_tgt = score_vdu_answer(res_target_only.final_answer, gt)
        stats["2_target_only_crop"]["correct_count"] += acc_tgt
        stats["2_target_only_crop"]["total_f1"] += f1_tgt
        stats["2_target_only_crop"]["total_tokens"] += (p_tok + c_tok + res_target_only.total_tokens)
        stats["2_target_only_crop"]["total_latency"] += (lat + res_target_only.latency)
        
        if res_target_only.assessment and res_target_only.assessment.valid:
            stats["2_target_only_crop"]["context_retained_count"] += 1
        else:
            stats["2_target_only_crop"]["context_lost_count"] += 1
            if res_target_only.assessment:
                for missing_k in res_target_only.assessment.missing_context:
                    stats["2_target_only_crop"]["lost_by_kind"][missing_k.value] += 1

        # -------------------------------------------------------------
        # Condition 3: CCEA_Context_Preserving (Crop with context retention)
        # -------------------------------------------------------------
        res_ccea = intervention.execute(
            image_path=img_path,
            query=q,
            client=client,
            evidence_region=evidence,
            initial_answer=ans_full,
            preserve_context=True  # Enforce context retention!
        )
        f1_ccea, acc_ccea = score_vdu_answer(res_ccea.final_answer, gt)
        stats["3_ccea_context_preserving"]["correct_count"] += acc_ccea
        stats["3_ccea_context_preserving"]["total_f1"] += f1_ccea
        stats["3_ccea_context_preserving"]["total_tokens"] += (p_tok + c_tok + res_ccea.total_tokens)
        stats["3_ccea_context_preserving"]["total_latency"] += (lat + res_ccea.latency)

        if res_ccea.assessment and res_ccea.assessment.valid:
            stats["3_ccea_context_preserving"]["context_retained_count"] += 1
        else:
            stats["3_ccea_context_preserving"]["context_lost_count"] += 1

        # -------------------------------------------------------------
        # Condition 4: CCEA_Cost_Aware_Controller (Adaptive decision policy)
        # -------------------------------------------------------------
        # Construct intermediate state
        state = GroundedState(
            c_plan=0.75,
            c_exec=0.70,
            c_judg=0.75,
            c_consensus=0.80,
            d_layout=0.25,
            d_evidence=0.20,
            current_answer=ans_full,
            b_remaining=2000,
            n_tokens_spent=p_tok + c_tok
        )
        chosen_action, meta = router.select_action(
            state,
            remaining_budget=2000,
            evidence_region=evidence,
            image_width=w,
            image_height=h
        )

        if chosen_action == Action.REGROUND:
            controller_decisions["acquire"] += 1
            final_ans_ctrl = res_ccea.final_answer
            tokens_ctrl = (p_tok + c_tok + res_ccea.total_tokens)
            lat_ctrl = lat + res_ccea.latency
            ctx_ok = res_ccea.assessment and res_ccea.assessment.valid
        elif chosen_action == Action.ABSTAIN:
            controller_decisions["abstain"] += 1
            final_ans_ctrl = "ABSTAIN_INSUFFICIENT_EVIDENCE"
            tokens_ctrl = (p_tok + c_tok)
            lat_ctrl = lat
            ctx_ok = False
        else:  # STOP
            controller_decisions["stop"] += 1
            final_ans_ctrl = ans_full
            tokens_ctrl = (p_tok + c_tok)
            lat_ctrl = lat
            ctx_ok = True

        f1_ctrl, acc_ctrl = score_vdu_answer(final_ans_ctrl, gt)
        stats["4_ccea_cost_aware_controller"]["correct_count"] += acc_ctrl
        stats["4_ccea_cost_aware_controller"]["total_f1"] += f1_ctrl
        stats["4_ccea_cost_aware_controller"]["total_tokens"] += tokens_ctrl
        stats["4_ccea_cost_aware_controller"]["total_latency"] += lat_ctrl
        if ctx_ok:
            stats["4_ccea_cost_aware_controller"]["context_retained_count"] += 1
        else:
            stats["4_ccea_cost_aware_controller"]["context_lost_count"] += 1

        # Collect detailed per-instance record for audit
        all_records.append({
            "instance_id": inst_id,
            "dataset": inst.get("dataset", "docvqa"),
            "query": q,
            "ground_truth": gt,
            "image_dimensions": [w, h],
            "target_box": list(evidence.target_box) if evidence.target_box else None,
            "conditions": {
                "1_full_overview": {
                    "prediction": ans_full,
                    "acc": acc_full,
                    "f1": f1_full,
                    "tokens": p_tok + c_tok,
                    "latency": round(lat, 4),
                    "cost_usd": round((p_tok + c_tok) * 0.00015 / 1000.0, 6)
                },
                "2_target_only_crop": {
                    "prediction": res_target_only.final_answer,
                    "crop_box": list(res_target_only.crop_box) if res_target_only.crop_box else None,
                    "retained_context": [c.value if hasattr(c, "value") else str(c) for c in res_target_only.retained_context],
                    "missing_context": [c.value if hasattr(c, "value") else str(c) for c in res_target_only.missing_context],
                    "acc": acc_tgt,
                    "f1": f1_tgt,
                    "tokens": p_tok + c_tok + res_target_only.total_tokens,
                    "latency": round(lat + res_target_only.latency, 4),
                    "cost_usd": round(res_target_only.cost_usd, 6)
                },
                "3_ccea_context_preserving": {
                    "prediction": res_ccea.final_answer,
                    "crop_box": list(res_ccea.crop_box) if res_ccea.crop_box else None,
                    "retained_context": [c.value if hasattr(c, "value") else str(c) for c in res_ccea.retained_context],
                    "missing_context": [c.value if hasattr(c, "value") else str(c) for c in res_ccea.missing_context],
                    "acc": acc_ccea,
                    "f1": f1_ccea,
                    "tokens": p_tok + c_tok + res_ccea.total_tokens,
                    "latency": round(lat + res_ccea.latency, 4),
                    "cost_usd": round(res_ccea.cost_usd, 6)
                },
                "4_ccea_cost_aware_controller": {
                    "chosen_action": chosen_action.value,
                    "prediction": final_ans_ctrl,
                    "acc": acc_ctrl,
                    "f1": f1_ctrl,
                    "tokens": tokens_ctrl,
                    "latency": round(lat_ctrl, 4),
                    "cost_usd": round(tokens_ctrl * 0.00015 / 1000.0, 6)
                }
            }
        })

    # Save detailed JSON records
    records_out = Path("discovery/live_validation/ccea_ablation_records.json")
    records_out.parent.mkdir(parents=True, exist_ok=True)
    with open(records_out, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2)
    print(f"[Artifact] Saved detailed per-instance ablation records to {records_out}")

    # -----------------------------------------------------------------
    # Print Comprehensive Ablation Report
    # -----------------------------------------------------------------
    N = len(instances)
    print("\n" + "=" * 90)
    print(f"ABLATION RESULTS TABLE (N = {N} instances)")
    print("=" * 90)
    print(f"{'Condition':<32} | {'Acc (%)':<8} | {'Avg F1':<8} | {'Tokens':<8} | {'Latency':<8} | {'Ctx Retained'}")
    print("-" * 90)

    for cond, s in stats.items():
        acc = (s["correct_count"] / N) * 100.0
        avg_f1 = s["total_f1"] / N
        avg_tok = round(s["total_tokens"] / N)
        avg_lat = round(s["total_latency"] / N, 3)
        ret_rate = f"{s['context_retained_count']}/{N} ({round(s['context_retained_count']/N*100)}%)"
        print(f"{cond:<32} | {acc:<8.1f} | {avg_f1:<8.3f} | {avg_tok:<8} | {avg_lat:<8}s | {ret_rate}")

    print("\n" + "-" * 90)
    print("CONTEXT LOSS BREAKDOWN IN UNCONSTRAINED TARGET CROP (Condition 2):")
    for kind, cnt in stats["2_target_only_crop"]["lost_by_kind"].items():
        if cnt > 0:
            print(f"  - {kind:<20}: {cnt} instances lost")
    print(f"\nController decisions (Condition 4): {controller_decisions}")
    print("=" * 90 + "\n")

    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_samples", type=int, default=5)
    parser.add_argument("--live", action="store_true", help="Execute genuine live API calls")
    args = parser.parse_args()

    run_ccea_ablation(num_samples=args.num_samples, use_live=args.live)
