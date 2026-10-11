import os
from openai import OpenAI
from gvoc_engine.config import MODELS

def list_models(provider_name, base_url, key):
    print(f"\n=== Available Models for {provider_name} ===")
    try:
        client = OpenAI(api_key=key, base_url=base_url)
        models = client.models.list()
        for m in models.data:
            m_id = m.id
            if any(term in m_id.lower() for term in ["vision", "vl", "flash", "pixtral", "llama-3.2", "gemini", "qwen"]):
                print(f"  - {m_id}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    groq_keys = MODELS.get("groq", {}).get("api_keys", [])
    if groq_keys:
        list_models("Groq", "https://api.groq.com/openai/v1", groq_keys[0])

    google_keys = MODELS.get("google", {}).get("api_keys", [])
    if google_keys:
        list_models("Google", "https://generativelanguage.googleapis.com/v1beta/openai/", google_keys[0])

    openrouter_keys = MODELS.get("openrouter", {}).get("api_keys", [])
    if openrouter_keys:
        list_models("OpenRouter", "https://openrouter.ai/api/v1", openrouter_keys[0])
