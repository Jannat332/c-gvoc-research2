"""
Isolated SQLite Database for Live Empirical Pilot.
Stores raw API calls, provenance metadata, and episode routing results.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional

DB_PATH = Path("discovery/live_validation/live_evaluation.db")

def init_live_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Table for individual live API calls
    cur.execute("""
    CREATE TABLE IF NOT EXISTS live_api_calls (
        call_id TEXT PRIMARY KEY,
        experiment_id TEXT NOT NULL,
        instance_id TEXT NOT NULL,
        method TEXT NOT NULL,
        call_role TEXT NOT NULL,
        dataset TEXT NOT NULL,
        split TEXT NOT NULL,
        provider TEXT NOT NULL,
        model_id TEXT NOT NULL,
        is_live_call INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        latency_sec REAL NOT NULL,
        status TEXT NOT NULL,
        attempt INTEGER NOT NULL,
        prompt_text TEXT NOT NULL,
        image_path TEXT,
        response_text TEXT,
        prompt_tokens INTEGER,
        completion_tokens INTEGER,
        total_tokens INTEGER,
        est_cost_usd REAL,
        error_msg TEXT
    )
    """)

    # Table for method episode outcomes
    cur.execute("""
    CREATE TABLE IF NOT EXISTS live_episode_results (
        episode_id TEXT PRIMARY KEY,
        experiment_id TEXT NOT NULL,
        instance_id TEXT NOT NULL,
        method TEXT NOT NULL,
        dataset TEXT NOT NULL,
        model_id TEXT NOT NULL,
        chosen_action TEXT NOT NULL,
        final_answer TEXT NOT NULL,
        is_correct INTEGER NOT NULL,
        is_abstain INTEGER NOT NULL,
        tokens_spent INTEGER NOT NULL,
        latency_sec REAL NOT NULL,
        est_cost_usd REAL,
        raw_telemetry TEXT,
        ground_truth TEXT NOT NULL,
        query TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def log_call(data: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO live_api_calls (
        call_id, experiment_id, instance_id, method, call_role, dataset, split,
        provider, model_id, is_live_call, timestamp, latency_sec, status, attempt,
        prompt_text, image_path, response_text, prompt_tokens, completion_tokens,
        total_tokens, est_cost_usd, error_msg
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["call_id"], data["experiment_id"], data["instance_id"], data["method"],
        data["call_role"], data["dataset"], data["split"], data["provider"],
        data["model_id"], 1 if data.get("is_live_call", True) else 0,
        data["timestamp"], data["latency_sec"], data["status"], data["attempt"],
        data["prompt_text"], data.get("image_path"), data.get("response_text"),
        data.get("prompt_tokens"), data.get("completion_tokens"), data.get("total_tokens"),
        data.get("est_cost_usd", 0.0), data.get("error_msg")
    ))
    conn.commit()
    conn.close()

def log_episode(data: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO live_episode_results (
        episode_id, experiment_id, instance_id, method, dataset, model_id,
        chosen_action, final_answer, is_correct, is_abstain, tokens_spent,
        latency_sec, est_cost_usd, raw_telemetry, ground_truth, query
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["episode_id"], data["experiment_id"], data["instance_id"], data["method"],
        data["dataset"], data["model_id"], data["chosen_action"], data["final_answer"],
        data["is_correct"], data["is_abstain"], data["tokens_spent"],
        data["latency_sec"], data.get("est_cost_usd", 0.0),
        json.dumps(data.get("raw_telemetry", {})),
        json.dumps(data.get("ground_truth", [])),
        data["query"]
    ))
    conn.commit()
    conn.close()
