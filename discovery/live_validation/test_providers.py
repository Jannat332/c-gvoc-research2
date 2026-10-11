import os
import sys
import time
from pathlib import Path
from openai import OpenAI
from gvoc_engine.config import MODELS

def test_provider(name, provider_type, base_url, model_name, api_keys):
    print(f"\n--- Testing {name} ({provider_type}) | Model: {model_name} ---")
    if not api_keys:
        print(f"FAILED: No API keys configured for {name}")
        return False, "No keys"
    
    key = api_keys[0]
    client = OpenAI(api_key=key, base_url=base_url)
    t0 = time.time()
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Return the single word: OK"}],
            max_tokens=10,
            temperature=0.0
        )
        dt = time.time() - t0
        content = response.choices[0].message.content.strip()
        usage = response.usage
        prompt_tok = usage.prompt_tokens if usage else None
        comp_tok = usage.completion_tokens if usage else None
        print(f"SUCCESS in {dt:.2f}s | Response: '{content}' | Usage: prompt={prompt_tok}, completion={comp_tok}")
        return True, content
    except Exception as e:
        dt = time.time() - t0
        print(f"FAILED in {dt:.2f}s | Error: {type(e).__name__}: {e}")
        return False, str(e)

if __name__ == "__main__":
    configs = [
        ("groq", "groq", "https://api.groq.com/openai/v1", "llama-3.2-11b-vision-preview"),
        ("google", "google", "https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-2.5-flash"),
        ("google_alt", "google", "https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-1.5-flash"),
        ("mistral", "mistral", "https://api.mistral.ai/v1", "pixtral-12b-2409"),
        ("openrouter", "openrouter", "https://openrouter.ai/api/v1", "qwen/qwen-2-vl-7b-instruct:free"),
    ]
    
    for name, p_type, url, model in configs:
        cfg = MODELS.get(p_type, {})
        keys = cfg.get("api_keys", [])
        test_provider(name, p_type, url, model, keys)
