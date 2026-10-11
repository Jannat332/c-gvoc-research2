import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect("discovery/live_validation/live_evaluation.db")
df_calls = pd.read_sql_query("SELECT * FROM live_api_calls", conn)
df_ep = pd.read_sql_query("SELECT * FROM live_episode_results", conn)
conn.close()

print("=== Latency Statistics (seconds) ===")
print(df_calls["latency_sec"].describe())

print("\n=== Prompt Tokens Statistics ===")
print(df_calls["prompt_tokens"].describe())

print("\n=== Completion Tokens Statistics ===")
print(df_calls["completion_tokens"].describe())

print("\n=== Total Tokens Statistics ===")
print(df_calls["total_tokens"].describe())

print("\n=== Null / Missing Checks ===")
for col in df_calls.columns:
    null_count = df_calls[col].isnull().sum()
    if null_count > 0:
        print(f"Column '{col}' has {null_count} nulls")
print("Null check complete across all columns.")

print("\n=== Check Duplicate Calls ===")
dups = df_calls.duplicated(subset=["call_id"]).sum()
print(f"Duplicate call_ids: {dups}")

print("\n=== Timestamp Monotonicity ===")
df_calls["dt"] = pd.to_datetime(df_calls["timestamp"])
print("First call timestamp:", df_calls["dt"].min())
print("Last call timestamp:", df_calls["dt"].max())
total_duration = (df_calls["dt"].max() - df_calls["dt"].min()).total_seconds()
print(f"Total experiment wall-clock duration: {total_duration:.1f} seconds ({total_duration/60:.2f} minutes)")

print("\n=== Latency vs Mock Verification ===")
min_lat = df_calls["latency_sec"].min()
print(f"Minimum latency: {min_lat:.3f}s (MockClient is ~0.05s; if min_lat > 0.5s, no MockClient calls occurred)")

print("\n=== Completeness Matrix (Instance x Method) ===")
completeness = df_ep.pivot(index="instance_id", columns="method", values="is_correct")
print(f"Shape of completeness matrix: {completeness.shape}")
print("Null values in completeness matrix:\n", completeness.isnull().sum())
