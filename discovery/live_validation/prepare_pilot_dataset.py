import os
import sys
import json
import time
import requests
from pathlib import Path

OUT_DIR = Path("discovery/live_validation/pilot_dataset")
IMG_DIR = OUT_DIR / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

def fetch_docvqa(n=50):
    print(f"Fetching {n} DocVQA test instances...")
    url = f"https://datasets-server.huggingface.co/rows?dataset=nielsr/docvqa_1200_examples&config=default&split=test&offset=0&limit={n}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()["rows"]
    instances = []
    
    for idx, item in enumerate(data):
        row = item["row"]
        inst_id = f"docvqa_{idx:03d}"
        q_en = row["query"].get("en") if isinstance(row["query"], dict) else str(row["query"])
        answers = row.get("answers", [])
        if not answers and "answer" in row:
            answers = [row["answer"]]
            
        img_info = row.get("image", {})
        img_url = img_info.get("src")
        img_file = IMG_DIR / f"{inst_id}.jpg"
        
        # Download image
        if not img_file.exists():
            img_r = requests.get(img_url, timeout=20)
            img_r.raise_for_status()
            with open(img_file, "wb") as f:
                f.write(img_r.content)
                
        instances.append({
            "instance_id": inst_id,
            "dataset": "docvqa",
            "source_split": "test",
            "source_index": idx,
            "query": q_en,
            "ground_truth": [str(a).strip() for a in answers],
            "image_path": str(img_file.resolve()),
            "width": img_info.get("width"),
            "height": img_info.get("height")
        })
    print(f"Successfully prepared {len(instances)} DocVQA instances.")
    return instances

def fetch_chartqa(n=50):
    print(f"Fetching {n} ChartQA test instances...")
    url = f"https://datasets-server.huggingface.co/rows?dataset=HuggingFaceM4/ChartQA&config=default&split=test&offset=0&limit={n}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()["rows"]
    instances = []
    
    for idx, item in enumerate(data):
        row = item["row"]
        inst_id = f"chartqa_{idx:03d}"
        q = row.get("query", "")
        labels = row.get("label", [])
        if isinstance(labels, str):
            labels = [labels]
            
        img_info = row.get("image", {})
        img_url = img_info.get("src")
        img_file = IMG_DIR / f"{inst_id}.png"
        
        # Download image
        if not img_file.exists():
            img_r = requests.get(img_url, timeout=20)
            img_r.raise_for_status()
            with open(img_file, "wb") as f:
                f.write(img_r.content)
                
        instances.append({
            "instance_id": inst_id,
            "dataset": "chartqa",
            "source_split": "test",
            "source_index": idx,
            "query": q,
            "ground_truth": [str(l).strip() for l in labels],
            "image_path": str(img_file.resolve()),
            "human_or_machine": row.get("human_or_machine", "human")
        })
    print(f"Successfully prepared {len(instances)} ChartQA instances.")
    return instances

if __name__ == "__main__":
    doc_insts = fetch_docvqa(50)
    chart_insts = fetch_chartqa(50)
    all_insts = doc_insts + chart_insts
    
    out_file = OUT_DIR / "instances.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_insts, f, indent=2)
    print(f"Total instances prepared: {len(all_insts)}. Saved to {out_file}")
