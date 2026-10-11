import sys
sys.path.append(".")
import time
from pathlib import Path
from openai import OpenAI
from gvoc_engine.config import MODELS

# Smoke test for diagnostic experiment
mistral_keys = MODELS.get("mistral", {}).get("api_keys", [])
assert len(mistral_keys) > 0, "No Mistral keys found"

client = OpenAI(api_key=mistral_keys[0], base_url="https://api.mistral.ai/v1", timeout=30.0)

# Test on chartqa_001.png
img_path = Path("discovery/live_validation/pilot_dataset/images/chartqa_001.png")
assert img_path.exists(), f"Image not found at {img_path}"

import base64
with open(img_path, "rb") as f:
    b64_data = base64.b64encode(f.read()).decode("utf-8")

prompt = "Answer the question directly and concisely based on the visual document or chart.\nQuestion: What is the difference in value between Lamb and Chicken?\nAnswer:"

t0 = time.time()
resp = client.chat.completions.create(
    model="pixtral-12b-2409",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_data}"}}
        ]
    }],
    max_tokens=60,
    temperature=0.0
)
dt = time.time() - t0

choice = resp.choices[0]
print(f"Smoke test successful in {dt:.2f}s!")
print(f"Finish reason: {choice.finish_reason}")
print(f"Content: {repr(choice.message.content)}")
print(f"Usage: prompt={resp.usage.prompt_tokens}, compl={resp.usage.completion_tokens}, total={resp.usage.total_tokens}")
