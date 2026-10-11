"""
Dedicated Live VLM Client for Empirical Validation.
CRITICAL RESEARCH INTEGRITY RULE: MockClient fallback is STRICTLY PROHIBITED.
Every call must be a genuine external API invocation or raise a verified error.
"""

import time
import base64
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from openai import OpenAI
from gvoc_engine.config import MODELS


class LiveAPIError(Exception):
    """Raised when live API call fails completely across all keys and retries."""
    pass


class LiveVLMClient:
    """Manages live API calls with key rotation, exponential backoff, and NO MOCK FALLBACK."""

    def __init__(self, provider: str = "mistral"):
        self.provider = provider.lower()
        if self.provider == "mistral":
            self.model_name = "pixtral-12b-2409"
            self.base_url = "https://api.mistral.ai/v1"
            self.api_keys = MODELS.get("mistral", {}).get("api_keys", [])
        elif self.provider in ["openrouter", "qwen"]:
            self.model_name = "qwen/qwen2.5-vl-72b-instruct"
            self.base_url = "https://openrouter.ai/api/v1"
            self.api_keys = MODELS.get("openrouter", {}).get("api_keys", [])
        else:
            raise ValueError(f"Unsupported live provider: {provider}")

        if not self.api_keys:
            raise LiveAPIError(f"No API keys available for provider {self.provider}")

        self.current_key_idx = 0

    def _rotate_key(self, reason: str = "Rate limit / 429"):
        if len(self.api_keys) > 1:
            prev = self.current_key_idx
            self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
            print(f"[Key Rotation] {self.provider.upper()}: Key #{prev+1} -> Key #{self.current_key_idx+1} ({reason})")

    def _get_client(self) -> OpenAI:
        key = self.api_keys[self.current_key_idx % len(self.api_keys)]
        return OpenAI(api_key=key, base_url=self.base_url, timeout=30.0)

    def call(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        max_tokens: int = 150,
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """
        Executes a genuine multimodal VLM API call.
        Returns detailed provenance dictionary including token counts, latency, and status.
        Raises LiveAPIError if the call cannot be completed.
        """
        content_items = [{"type": "text", "text": prompt}]
        if image_path:
            p = Path(image_path)
            if not p.exists():
                raise FileNotFoundError(f"Image not found at {image_path}")
            with open(p, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode("utf-8")
            ext = p.suffix.lower().replace(".", "")
            mime = "image/png" if ext == "png" else "image/jpeg"
            content_items.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64_data}"}
            })

        messages = [{"role": "user", "content": content_items}]
        max_retries = max(4, len(self.api_keys) * 2)
        backoff = 1.0
        last_error = None

        for attempt in range(max_retries):
            t0 = time.time()
            client = self._get_client()
            try:
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                latency = time.time() - t0
                raw_text = response.choices[0].message.content or ""
                usage = response.usage
                
                return {
                    "status": "success",
                    "text": raw_text.strip(),
                    "prompt_tokens": usage.prompt_tokens if usage else None,
                    "completion_tokens": usage.completion_tokens if usage else None,
                    "total_tokens": usage.total_tokens if usage else None,
                    "latency_sec": latency,
                    "model_id": self.model_name,
                    "provider": self.provider,
                    "attempt": attempt + 1,
                    "is_live_call": True
                }
            except Exception as e:
                latency = time.time() - t0
                err_str = str(e).lower()
                last_error = e
                is_rate_limit = any(t in err_str for t in ["429", "rate limit", "quota", "exhausted"])
                self._rotate_key(reason=type(e).__name__)
                if is_rate_limit:
                    time.sleep(backoff)
                    backoff = min(backoff * 2.0, 8.0)
                else:
                    time.sleep(0.5)

        raise LiveAPIError(f"Failed to execute live call for {self.model_name} after {max_retries} attempts: {last_error}")
