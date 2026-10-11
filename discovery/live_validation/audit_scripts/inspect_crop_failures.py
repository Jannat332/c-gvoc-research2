import sqlite3
import pandas as pd
from PIL import Image
from pathlib import Path

conn = sqlite3.connect("discovery/live_validation/confirmatory_experiment/confirmatory_evaluation.db")
df = pd.read_sql_query("SELECT * FROM confirmatory_results", conn)
conn.close()

piv = df.pivot(index="instance_id", columns="condition_id", values="is_correct")
c4_sub = df[df["condition_id"] == "C4"].set_index("instance_id")
c1_sub = df[df["condition_id"] == "C1"].set_index("instance_id")

# All C4 failures
c4_failures = c4_sub[c4_sub["is_correct"] == 0].index.tolist()
print(f"Total C4 failures: {len(c4_failures)}")

for inst_id in c4_failures:
    row4 = c4_sub.loc[inst_id]
    row1 = c1_sub.loc[inst_id]
    q = row4["prompt_text"].split("Question: ")[1].split("\nAnswer:")[0].strip()
    gt = row4["ground_truth"]
    ans4 = row4["response_text"]
    ans1 = row1["response_text"]
    corr1 = row1["is_correct"]
    
    orig_img_path = Path("discovery/live_validation/pilot_dataset/images") / (f"{inst_id}.jpg" if row4["dataset"] == "docvqa" else f"{inst_id}.png")
    crop_img_path = Path("discovery/live_validation/confirmatory_experiment/transformed_images") / f"{inst_id}_crop.png"
    
    orig_img = Image.open(orig_img_path)
    crop_img = Image.open(crop_img_path)
    
    print(f"\n=======================================================")
    print(f"[{inst_id}] ({row4['dataset'].upper()})")
    print(f"Q:  {q}")
    print(f"GT: {gt}")
    print(f"C1 (Full Image Native): corr={corr1}, ans='{ans1}'")
    print(f"C4 (Center 50% Crop):   corr=0, ans='{ans4}'")
    print(f"Original Dimensions:    {orig_img.size}")
    print(f"Crop Dimensions:        {crop_img.size} (Box: [0.25w, 0.25h, 0.75w, 0.75h])")
