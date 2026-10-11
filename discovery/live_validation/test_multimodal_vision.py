import os
import sys
import time
import base64
from pathlib import Path
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
from gvoc_engine.config import MODELS

# Create a small synthetic test image to test multimodal vision inference
test_img_path = Path("discovery/live_validation/test_document.png")
test_img_path.parent.mkdir(parents=True, exist_ok=True)

img = Image.new('RGB', (400, 200), color=(255, 255, 255))
d = ImageDraw.Draw(img)
d.rectangle([10, 10, 390, 190], outline=(0, 0, 0), width=2)
d.text((30, 40), "INVOICE #INV-88219", fill=(0, 0, 0))
d.text((30, 80), "Total Balance Due: $1,450.00", fill=(0, 0, 0))
d.text((30, 120), "Due Date: 2026-11-15", fill=(0, 0, 0))
img.save(test_img_path)

with open(test_img_path, "rb") as f:
    b64_img = base64.b64encode(f.read()).decode("utf-8")

def test_vlm(name, client, model_id):
    print(f"\n--- Testing VLM: {name} (Model: {model_id}) ---")
    prompt = "What is the Total Balance Due shown on this invoice? Give only the dollar amount."
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64_img}"}
                }
            ]
        }
    ]
    t0 = time.time()
    try:
        resp = client.chat.completions.create(
            model=model_id,
            messages=messages,
            max_tokens=50,
            temperature=0.0
        )
        dt = time.time() - t0
        ans = resp.choices[0].message.content.strip()
        usage = resp.usage
        p_tok = usage.prompt_tokens if usage else None
        c_tok = usage.completion_tokens if usage else None
        print(f"SUCCESS in {dt:.2f}s | Answer: '{ans}' | prompt_tokens={p_tok}, completion_tokens={c_tok}")
        return True
    except Exception as e:
        dt = time.time() - t0
        print(f"FAILED in {dt:.2f}s | Error: {type(e).__name__}: {e}")
        return False

# 1. Mistral
mistral_key = MODELS.get("mistral", {}).get("api_keys", [])[0]
c_mistral = OpenAI(api_key=mistral_key, base_url="https://api.mistral.ai/v1")
test_vlm("Mistral Pixtral", c_mistral, "pixtral-12b-2409")

# 2. Google
google_key = MODELS.get("google", {}).get("api_keys", [])[0]
c_google = OpenAI(api_key=google_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
for m in ["gemini-2.5-flash", "models/gemini-2.5-flash"]:
    if test_vlm(f"Google ({m})", c_google, m):
        break

# 3. OpenRouter
openrouter_key = MODELS.get("openrouter", {}).get("api_keys", [])[0]
c_openrouter = OpenAI(api_key=openrouter_key, base_url="https://openrouter.ai/api/v1")
test_vlm("OpenRouter Qwen2.5-VL-72B", c_openrouter, "qwen/qwen2.5-vl-72b-instruct")
