"""
Row-Level & Grouped Provenance Audit for GVoC Evaluation Database.
"""

import sqlite3
from pathlib import Path

db_path = Path("gvoc_engine/gvoc_evaluation.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("=" * 105)
print(" GROUPED PROVENANCE BREAKDOWN OF task_evaluations (TOTAL ROWS: 16,606)")
print("=" * 105)

cur.execute("""
SELECT 
    baseline_type,
    model_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT instance_id) as unique_instances,
    SUM(CASE WHEN final_answer LIKE '%Direct extraction%' THEN 1 ELSE 0 END) as mock_rows,
    SUM(CASE WHEN final_answer NOT LIKE '%Direct extraction%' THEN 1 ELSE 0 END) as other_rows,
    ROUND(AVG(is_correct)*100, 2) as acc_pct,
    ROUND(AVG(total_prompt_tokens + total_completion_tokens), 1) as avg_tokens
FROM task_evaluations
GROUP BY baseline_type, model_name
ORDER BY baseline_type, model_name
""")

rows = cur.fetchall()
print(f"{'Baseline':<18} | {'Model Name':<28} | {'Rows':<6} | {'Uniq':<6} | {'Mock':<6} | {'Other':<6} | {'Acc (%)':<8} | {'Tokens':<8}")
print("-" * 105)
for r in rows:
    print(f"{r[0]:<18} | {r[1]:<28} | {r[2]:<6} | {r[3]:<6} | {r[4]:<6} | {r[5]:<6} | {r[6]:>7.2f}% | {r[7]:>7.1f}")
print("=" * 105)

# Breakdown of unique query questions in JSONL files vs database
cur.execute("SELECT DISTINCT dataset, COUNT(DISTINCT instance_id) FROM task_evaluations GROUP BY dataset")
print("\nDatabase Unique Instance Count by Domain:")
for r in cur.fetchall():
    print(f"  {r[0]:<15}: {r[1]} unique instance IDs")

conn.close()
