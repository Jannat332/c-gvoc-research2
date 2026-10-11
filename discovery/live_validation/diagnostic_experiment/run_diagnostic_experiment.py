import sys
sys.path.append(".")
import os
import time
import json
import sqlite3
import base64
from pathlib import Path
from typing import Dict, Any
from openai import OpenAI
from gvoc_engine.config import MODELS
from discovery.live_validation.scoring import score_vdu_answer

# Output DB
DB_PATH = Path("discovery/live_validation/diagnostic_experiment/diagnostic_evaluation.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# 1. Initialize SQLite Database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS diagnostic_results (
    call_id TEXT PRIMARY KEY,
    instance_id TEXT NOT NULL,
    subset_type TEXT NOT NULL,
    condition TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    max_tokens INTEGER NOT NULL,
    response_text TEXT NOT NULL,
    finish_reason TEXT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    latency_sec REAL,
    is_correct INTEGER,
    score REAL,
    ground_truth TEXT,
    timestamp TEXT
)
""")
conn.commit()

# 2. Select Diagnostic Subset
# Pre-declared Harmful (N=6) and Comparison (N=6: 3 beneficial, 3 stable correct)
DIAGNOSTIC_INSTANCES = [
    # Harmful
    {"instance_id": "chartqa_001", "subset_type": "harmful"},
    {"instance_id": "chartqa_014", "subset_type": "harmful"},
    {"instance_id": "chartqa_022", "subset_type": "harmful"},
    {"instance_id": "chartqa_027", "subset_type": "harmful"},
    {"instance_id": "chartqa_039", "subset_type": "harmful"},
    {"instance_id": "chartqa_041", "subset_type": "harmful"},
    # Beneficial
    {"instance_id": "chartqa_017", "subset_type": "beneficial"},
    {"instance_id": "chartqa_018", "subset_type": "beneficial"},
    {"instance_id": "chartqa_038", "subset_type": "beneficial"},
    # Stable Correct
    {"instance_id": "chartqa_003", "subset_type": "stable_correct"},
    {"instance_id": "chartqa_004", "subset_type": "stable_correct"},
    {"instance_id": "chartqa_005", "subset_type": "stable_correct"},
]

# Load full instance metadata from preregistered_100.json
with open("discovery/live_validation/pilot_dataset/preregistered_100.json", "r") as f:
    all_instances = {item["instance_id"]: item for item in json.load(f)}

# 3. Setup Client
mistral_keys = MODELS.get("mistral", {}).get("api_keys", [])
assert len(mistral_keys) > 0, "No Mistral keys found"
key_idx = 0

def call_vlm(prompt: str, img_path: Path, max_tokens: int) -> Dict[str, Any]:
    global key_idx
    with open(img_path, "rb") as f:
        b64_data = base64.b64encode(f.read()).decode("utf-8")
    
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_data}"}}
        ]
    }]

    for attempt in range(6):
        curr_key = mistral_keys[key_idx % len(mistral_keys)]
        client = OpenAI(api_key=curr_key, base_url="https://api.mistral.ai/v1", timeout=35.0)
        t0 = time.time()
        try:
            resp = client.chat.completions.create(
                model="pixtral-12b-2409",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.0
            )
            dt = time.time() - t0
            choice = resp.choices[0]
            usage = resp.usage
            return {
                "text": choice.message.content.strip() if choice.message.content else "",
                "finish_reason": choice.finish_reason,
                "prompt_tokens": usage.prompt_tokens if usage else None,
                "completion_tokens": usage.completion_tokens if usage else None,
                "total_tokens": usage.total_tokens if usage else None,
                "latency_sec": dt
            }
        except Exception as e:
            err = str(e)
            print(f"[Warning] Attempt {attempt+1} failed: {err}. Rotating key...")
            key_idx = (key_idx + 1) % len(mistral_keys)
            time.sleep(1.0)
    raise RuntimeError(f"Failed to execute call after 6 attempts")

# 4. Conditions Definition
# A. Direct inference with original prompt, original token budget (60)
# B. Original intervention prompt with original intervention token budget (60)
# C. Original intervention prompt with larger token budget (256)
# D. Concise intervention prompt with original intervention token budget (60)
# E. Concise intervention prompt with larger token budget (256)

CONDITIONS = {
    "A": {
        "desc": "Direct inference (orig prompt, 60 tokens)",
        "prompt_fn": lambda q: f"Answer the question directly and concisely based on the visual document or chart.\nQuestion: {q}\nAnswer:",
        "max_tokens": 60
    },
    "B": {
        "desc": "Original intervention prompt (orig 60 tokens)",
        "prompt_fn": lambda q: f"Examine the document/chart carefully with high precision around the relevant visual area to answer accurately.\nQuestion: {q}\nAnswer:",
        "max_tokens": 60
    },
    "C": {
        "desc": "Original intervention prompt (larger 256 tokens)",
        "prompt_fn": lambda q: f"Examine the document/chart carefully with high precision around the relevant visual area to answer accurately.\nQuestion: {q}\nAnswer:",
        "max_tokens": 256
    },
    "D": {
        "desc": "Concise intervention prompt (orig 60 tokens)",
        "prompt_fn": lambda q: f"Examine the visual document or chart carefully around the relevant area. State only the direct, concise final answer without introductory explanation.\nQuestion: {q}\nAnswer:",
        "max_tokens": 60
    },
    "E": {
        "desc": "Concise intervention prompt (larger 256 tokens)",
        "prompt_fn": lambda q: f"Examine the visual document or chart carefully around the relevant area. State only the direct, concise final answer without introductory explanation.\nQuestion: {q}\nAnswer:",
        "max_tokens": 256
    }
}

print(f"Starting Diagnostic Experiment across {len(DIAGNOSTIC_INSTANCES)} instances and {len(CONDITIONS)} conditions ({len(DIAGNOSTIC_INSTANCES)*len(CONDITIONS)} total calls)...")

import datetime

for i, diag in enumerate(DIAGNOSTIC_INSTANCES):
    inst_id = diag["instance_id"]
    stype = diag["subset_type"]
    meta = all_instances[inst_id]
    q = meta["query"]
    gt = meta["ground_truth"]
    img_path = Path("discovery/live_validation/pilot_dataset/images") / f"{inst_id}.png"
    
    print(f"\n[{i+1}/{len(DIAGNOSTIC_INSTANCES)}] Instance {inst_id} ({stype}): '{q[:50]}...'")

    for cond_key, cond_info in CONDITIONS.items():
        call_id = f"diag_{inst_id}_{cond_key}"
        
        # Check if already in DB
        cursor.execute("SELECT call_id FROM diagnostic_results WHERE call_id = ?", (call_id,))
        if cursor.fetchone() is not None:
            print(f"  Condition {cond_key}: already evaluated, skipping.")
            continue
            
        p_text = cond_info["prompt_fn"](q)
        max_tok = cond_info["max_tokens"]
        
        res = call_vlm(p_text, img_path, max_tok)
        ans = res["text"]
        f1, is_corr = score_vdu_answer(ans, gt)
        
        cursor.execute("""
        INSERT INTO diagnostic_results (
            call_id, instance_id, subset_type, condition, prompt_text, max_tokens,
            response_text, finish_reason, prompt_tokens, completion_tokens,
            total_tokens, latency_sec, is_correct, score, ground_truth, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            call_id, inst_id, stype, cond_key, p_text, max_tok,
            ans, res["finish_reason"], res["prompt_tokens"], res["completion_tokens"],
            res["total_tokens"], res["latency_sec"], is_corr, f1, json.dumps(gt),
            datetime.datetime.now().isoformat()
        ))
        conn.commit()
        
        print(f"  Condition {cond_key} (max={max_tok:3d}): tokens={res['completion_tokens']:3d}, finish={res['finish_reason']}, corr={is_corr}, resp='{ans[:40]}...'")
        time.sleep(0.3)

conn.close()
print("\nDiagnostic experiment completed successfully and committed to DB.")
