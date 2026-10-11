"""
Check API environment without printing secret key values.
"""
from gvoc_engine.config import MODELS, SECURE_TOKENS_PATH
import os

print(f"SECURE_TOKENS_PATH: {SECURE_TOKENS_PATH}")
print(f"File exists: {SECURE_TOKENS_PATH.exists()}")

print("\nModel configurations in config.py:")
for model_id, cfg in MODELS.items():
    key_count = len(cfg.get("api_keys", []))
    print(f"  {model_id:<12} | Provider: {cfg.get('provider'):<10} | Model: {cfg.get('model_name'):<30} | Keys: {key_count}")

# Check key names present in os.environ (only names, never values)
print("\nRelevant API key environment variables detected:")
for env_var in sorted(os.environ.keys()):
    if any(term in env_var.upper() for term in ["API_KEY", "OPENAI", "GEMINI", "GOOGLE", "GROQ", "MISTRAL", "OPENROUTER"]):
        val_len = len(os.environ[env_var])
        print(f"  {env_var}: present (length: {val_len})")
