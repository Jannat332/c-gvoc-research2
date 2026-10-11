import sqlite3
import pandas as pd
from pathlib import Path

db_path = Path("discovery/live_validation/live_evaluation.db")
conn = sqlite3.connect(db_path)

print("=== Tables in live_evaluation.db ===")
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for t in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM {t[0]}").fetchone()[0]
    print(f"Table: {t[0]:<30} Rows: {count}")

print("\n=== Calls Breakdown ===")
df_calls = pd.read_sql_query("SELECT * FROM live_api_calls", conn)
print("Total calls:", len(df_calls))
print("Status counts:\n", df_calls["status"].value_counts())
print("\nProvider counts:\n", df_calls["provider"].value_counts())
print("\nModel counts:\n", df_calls["model_id"].value_counts())
print("\nCall roles:\n", df_calls["call_role"].value_counts())
print("\nAttempt distribution:\n", df_calls["attempt"].value_counts())
print("\nIs live call counts:\n", df_calls["is_live_call"].value_counts())
print("Unique instances in calls:", df_calls["instance_id"].nunique())

print("\n=== Episodes Breakdown ===")
df_ep = pd.read_sql_query("SELECT * FROM live_episode_results", conn)
print("Total episodes:", len(df_ep))
print("Methods in episodes:\n", df_ep["method"].value_counts())
print("Unique instances in episodes:", df_ep["instance_id"].nunique())
print("Instances per method:\n", df_ep.groupby("method")["instance_id"].nunique())

print("\n=== Diagnostic Actions Breakdown ===")
df_diag = pd.read_sql_query("SELECT * FROM live_counterfactual_actions", conn)
print("Total diagnostic action rows:", len(df_diag))
print("Actions in diagnostics:\n", df_diag["action"].value_counts())
print("Unique instances in diagnostics:", df_diag["instance_id"].nunique())

conn.close()
