import sys
sys.path.append(".")
import os
import time
import json
import sqlite3
import base64
from pathlib import Path
from typing import Dict, Any
from PIL import Image
from openai import OpenAI
from gvoc_engine.config import MODELS
from discovery.live_validation.scoring import score_vdu_answer

# Output Paths
EXP_DIR = Path("discovery/live_validation/confirmatory_experiment")
EXP_DIR.mkdir(parents=True, exist_ok=True)
TRANSFORM_DIR = EXP_DIR / "transformed_images"
TRANSFORM_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = EXP_DIR / "confirmatory_evaluation.db"

# 1. Initialize SQLite Database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS confirmatory_results (
    call_id TEXT PRIMARY KEY,
    instance_id TEXT NOT NULL,
    dataset TEXT NOT NULL,
    condition_id TEXT NOT NULL,
    condition_name TEXT NOT NULL,
    observation_type TEXT NOT NULL,
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
    image_path TEXT,
    timestamp TEXT
)
""")
conn.commit()

# 2. Select the 20 Untouched Preregistered Confirmatory Instances
TARGET_INSTANCE_IDS = [f"docvqa_0{i:02d}" for i in range(10, 20)] + [f"chartqa_0{i:02d}" for i in range(10, 20)]

with open("discovery/live_validation/pilot_dataset/preregistered_100.json", "r") as f:
    all_instances = {item["instance_id"]: item for item in json.load(f)}

# 3. Setup Client with Key Rotation
mistral_keys = MODELS.get("mistral", {}).get("api_keys", [])
assert len(mistral_keys) > 0, "No Mistral keys found"
key_idx = 0

def call_vlm(prompt: str, img_path: Path, max_tokens: int) -> Dict[str, Any]:
    global key_idx
    with open(img_path, "rb") as f:
        b64_data = base64.b64encode(f.read()).decode("utf-8")
    
    ext = img_path.suffix.lower().replace(".", "")
    mime = "image/png" if ext == "png" else "image/jpeg"

    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64_data}"}}
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

# 4. Define Preregistered Conditions
# Prompts
P_CONC = lambda q: f"Examine the visual document or chart carefully. State only the direct, concise final answer on the last line without introductory explanation.\nQuestion: {q}\nAnswer:"
P_CONV = lambda q: f"Examine the document/chart carefully with high precision around the relevant visual area. Think step-by-step to answer accurately.\nQuestion: {q}\nAnswer:"

CONDITIONS = {
    "C1": {
        "name": "Full_Direct",
        "obs": "full",
        "prompt_fn": P_CONC,
        "max_tokens": 60
    },
    "C2": {
        "name": "Degraded_Direct",
        "obs": "low",
        "prompt_fn": P_CONC,
        "max_tokens": 60
    },
    "C3": {
        "name": "Degraded_Reasoning",
        "obs": "low",
        "prompt_fn": P_CONV,
        "max_tokens": 256
    },
    "C4": {
        "name": "Crop_Observation",
        "obs": "crop",
        "prompt_fn": P_CONC,
        "max_tokens": 60
    },
    "C5": {
        "name": "Full_Conversational_60",
        "obs": "full",
        "prompt_fn": P_CONV,
        "max_tokens": 60
    }
}

print(f"Starting Confirmatory Experiment: {len(TARGET_INSTANCE_IDS)} instances x {len(CONDITIONS)} conditions = {len(TARGET_INSTANCE_IDS)*len(CONDITIONS)} total calls.")

import datetime

for i, inst_id in enumerate(TARGET_INSTANCE_IDS):
    meta = all_instances[inst_id]
    q = meta["query"]
    gt = meta["ground_truth"]
    dset = meta["dataset"]
    
    # Locate original image
    img_orig_path = Path("discovery/live_validation/pilot_dataset/images") / (f"{inst_id}.jpg" if dset == "docvqa" else f"{inst_id}.png")
    assert img_orig_path.exists(), f"Missing original image: {img_orig_path}"
    
    # Prepare image transformations
    # 1. Full Image
    path_full = img_orig_path
    
    # 2. Degraded (320x320)
    path_low = TRANSFORM_DIR / f"{inst_id}_low.png"
    if not path_low.exists():
        img = Image.open(img_orig_path).convert("RGB")
        img_low = img.resize((320, 320), Image.Resampling.BILINEAR)
        img_low.save(path_low)
        
    # 3. High-res Crop (center 50% region)
    path_crop = TRANSFORM_DIR / f"{inst_id}_crop.png"
    if not path_crop.exists():
        img = Image.open(img_orig_path).convert("RGB")
        w, h = img.size
        crop_box = (int(0.25 * w), int(0.25 * h), int(0.75 * w), int(0.75 * h))
        img_crop = img.crop(crop_box)
        img_crop.save(path_crop)
        
    image_paths_by_obs = {
        "full": path_full,
        "low": path_low,
        "crop": path_crop
    }
    
    print(f"\n[{i+1}/{len(TARGET_INSTANCE_IDS)}] Instance {inst_id} ({dset}): '{q[:50]}...'")

    for cond_id, cond in CONDITIONS.items():
        call_id = f"conf_{inst_id}_{cond_id}"
        
        # Check DB
        cursor.execute("SELECT call_id FROM confirmatory_results WHERE call_id = ?", (call_id,))
        if cursor.fetchone() is not None:
            print(f"  Condition {cond_id} ({cond['name']}): already completed, skipping.")
            continue
            
        p_text = cond["prompt_fn"](q)
        max_tok = cond["max_tokens"]
        cur_img = image_paths_by_obs[cond["obs"]]
        
        res = call_vlm(p_text, cur_img, max_tok)
        ans = res["text"]
        f1, is_corr = score_vdu_answer(ans, gt)
        
        cursor.execute("""
        INSERT INTO confirmatory_results (
            call_id, instance_id, dataset, condition_id, condition_name,
            observation_type, prompt_text, max_tokens, response_text,
            finish_reason, prompt_tokens, completion_tokens, total_tokens,
            latency_sec, is_correct, score, ground_truth, image_path, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            call_id, inst_id, dset, cond_id, cond["name"],
            cond["obs"], p_text, max_tok, ans,
            res["finish_reason"], res["prompt_tokens"], res["completion_tokens"],
            res["total_tokens"], res["latency_sec"], is_corr, f1,
            json.dumps(gt), str(cur_img), datetime.datetime.now().isoformat()
        ))
        conn.commit()
        
        print(f"  {cond_id:2s} ({cond['name']:20s}): tok={res['completion_tokens']:3d}, fin={res['finish_reason']:6s}, corr={is_corr}, ans='{ans[:40]}...'")
        time.sleep(0.25)

conn.close()
print("\nConfirmatory Experiment completed successfully and recorded to DB.")
