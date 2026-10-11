import json
from pathlib import Path
from collections import Counter

inst_file = Path("discovery/live_validation/pilot_dataset/preregistered_100.json")
with open(inst_file, "r", encoding="utf-8") as f:
    instances = json.load(f)

print(f"Total instances in preregistered list: {len(instances)}")

# Check DocVQA duplicate images or questions
doc_instances = [x for x in instances if x["dataset"] == "docvqa"]
chart_instances = [x for x in instances if x["dataset"] == "chartqa"]

print(f"\nDocVQA count: {len(doc_instances)}")
print(f"ChartQA count: {len(chart_instances)}")

# Check queries
doc_queries = [x["query"] for x in doc_instances]
chart_queries = [x["query"] for x in chart_instances]
print(f"Unique DocVQA queries: {len(set(doc_queries))} / {len(doc_queries)}")
print(f"Unique ChartQA queries: {len(set(chart_queries))} / {len(chart_queries)}")

# Check image file sizes / content hashes
import hashlib
def get_file_hash(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

doc_hashes = [get_file_hash(x["image_path"]) for x in doc_instances]
chart_hashes = [get_file_hash(x["image_path"]) for x in chart_instances]
print(f"Unique DocVQA image hashes: {len(set(doc_hashes))} / {len(doc_hashes)}")
print(f"Unique ChartQA image hashes: {len(set(chart_hashes))} / {len(chart_hashes)}")

# Examine duplicate image occurrences in DocVQA
hash_counts = Counter(doc_hashes)
multipage_doc_counts = {h: c for h, c in hash_counts.items() if c > 1}
print(f"Number of distinct images appearing multiple times in DocVQA: {len(multipage_doc_counts)}")
for h, c in multipage_doc_counts.items():
    matching_insts = [inst["instance_id"] for inst, hsh in zip(doc_instances, doc_hashes) if hsh == h]
    print(f"  Image hash {h[:8]} appears {c} times across instances: {matching_insts}")

# Check scoring convention
print("\nSample DocVQA questions and ground truths:")
for x in doc_instances[:5]:
    print(f"  [{x['instance_id']}] Q: {x['query']} | GT: {x['ground_truth']}")

print("\nSample ChartQA questions and ground truths:")
for x in chart_instances[:5]:
    print(f"  [{x['instance_id']}] Q: {x['query']} | GT: {x['ground_truth']}")
