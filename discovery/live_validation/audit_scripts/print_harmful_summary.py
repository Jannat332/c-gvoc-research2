import json

with open("discovery/live_validation/audit_scripts/chartqa_harmful_details.json") as f:
    d = json.load(f)

for k, v in d.items():
    print(f"\n=== {k} ===")
    print("Query:", v["query"])
    print("GT:", v["ground_truth"])
    print("Monolithic:", v["methods"]["monolithic"])
    print("C-GVoC:", v["methods"]["cgvoc"])
    print("GVoC:", v["methods"]["gvoc"])
    print("Oracle:", v["methods"]["oracle"])
    for c in v["calls"]:
        print(f"  [{c['role']} | tokens={c['tokens']}]: {repr(c['response'])}")
