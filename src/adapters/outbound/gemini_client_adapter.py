"""
Outbound Adapter: Google Gemini SaaS API Adapter.
Implements ILLMClient using Python standard library urllib (Zero External Dependencies).
Supports Gemini 2.0 / 2.5 Multi-Tier Lineup (Pro, Flash, Flash-Lite, Flash Thinking),
Thinking Budget configuration, Context Caching, and Structured JSON Schema outputs.
"""

from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional
from src.ports.outbound.llm_client_port import ILLMClient
from src.domain.exceptions import ModelInferenceError


class GeminiClientAdapter(ILLMClient):
    """
    Concrete implementation of ILLMClient for Google Gemini Cloud SaaS API.
    Interacts with the Google Generative Language REST API (v1beta).
    """

    KNOWN_MODELS = [
        {"name": "gemini-2.5-pro", "role": "Macro Architecture & Strategic Orchestration", "tier": "Tier 3 Cloud Pro"},
        {"name": "gemini-2.5-flash", "role": "Broad Context & Multi-Agent Concurrency", "tier": "Tier 2 Cloud Flash"},
        {"name": "gemini-2.0-flash-thinking-exp", "role": "Deep CoT Reasoning & Discrepancy Resolution", "tier": "Tier 2.5 Flash Thinking"},
        {"name": "gemini-2.0-flash-lite", "role": "Fast Triage, Linting & Micro-Validation", "tier": "Tier 1 Cloud Flash-Lite"},
        {"name": "text-embedding-004", "role": "Cloud Vector Embeddings (768-dim)", "tier": "Cloud RAG"},
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        timeout: float = 45.0,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get_api_key(self) -> str:
        key = self.api_key or os.getenv("GEMINI_API_KEY", "")
        if not key:
            raise ModelInferenceError(
                "Gemini API key is not configured. Set GEMINI_API_KEY environment variable or pass api_key to adapter."
            )
        return key

    def generate(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        response_format: Optional[str | Dict[str, Any]] = None,
        thinking_budget: Optional[int] = None,
        cached_content: Optional[str] = None,
    ) -> str:
        """
        Invokes Gemini generateContent REST endpoint.
        Supports thinking budget, system instructions, and schema-constrained outputs.
        """
        key = self._get_api_key()

        # Sanitize model name (strip "models/" prefix if present)
        clean_model = model.replace("models/", "")

        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        payload: Dict[str, Any] = {"contents": contents}

        # 1. System Prompt / Instructions
        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        # 2. Generation Config
        gen_config: Dict[str, Any] = {"temperature": temperature}

        # Thinking Budget (Gemini 2.0 Flash Thinking / 2.5 Pro)
        if thinking_budget is not None and thinking_budget > 0:
            gen_config["thinkingConfig"] = {"thinkingBudget": thinking_budget}

        # Structured Outputs (JSON Schema parity with BNF local decoding)
        if response_format:
            if isinstance(response_format, dict):
                gen_config["responseMimeType"] = "application/json"
                gen_config["responseSchema"] = response_format
            elif isinstance(response_format, str) and response_format.lower() == "json":
                gen_config["responseMimeType"] = "application/json"

        if gen_config:
            payload["generationConfig"] = gen_config

        # 3. Context Caching Support
        if cached_content:
            payload["cachedContent"] = cached_content

        endpoint = f"{self.base_url}/models/{clean_model}:generateContent?key={key}"
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if not candidates:
                    return ""
                parts = candidates[0].get("content", {}).get("parts", [])
                # Extract text parts (excluding pure thought parts if separated)
                text_segments = [p.get("text", "") for p in parts if "text" in p]
                return "".join(text_segments).strip()
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8") if e.fp else ""
            raise ModelInferenceError(
                f"Gemini API HTTP {e.code} error for model {clean_model}: {e.reason} - {err_body[:300]}"
            ) from e
        except Exception as e:
            raise ModelInferenceError(f"Gemini generateContent call failed for {clean_model}: {e}") from e

    def embed(self, text: str, model: str = "text-embedding-004") -> List[float]:
        """Generates embedding vector using Gemini embedContent endpoint."""
        key = self._get_api_key()
        clean_model = model.replace("models/", "")
        endpoint = f"{self.base_url}/models/{clean_model}:embedContent?key={key}"

        payload = {
            "model": f"models/{clean_model}",
            "content": {"parts": [{"text": text}]},
        }

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=20.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("embedding", {}).get("values", [])
        except Exception as e:
            raise ModelInferenceError(f"Gemini embedContent failed for {clean_model}: {e}") from e

    def list_models(self) -> List[Dict[str, Any]]:
        """Lists available Gemini models from API or falls back to known models."""
        try:
            key = self._get_api_key()
            endpoint = f"{self.base_url}/models?key={key}"
            req = urllib.request.Request(endpoint, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = []
                for m in data.get("models", []):
                    name = m.get("name", "").replace("models/", "")
                    models.append({
                        "name": name,
                        "display_name": m.get("displayName", name),
                        "supported_methods": m.get("supportedGenerationMethods", []),
                        "input_token_limit": m.get("inputTokenLimit", 0),
                        "output_token_limit": m.get("outputTokenLimit", 0),
                    })
                return models if models else self.KNOWN_MODELS
        except Exception:
            return self.KNOWN_MODELS

    def create_cached_content(
        self,
        content: str,
        model: str = "gemini-2.5-pro",
        ttl_seconds: int = 3600,
        display_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates a CachedContent resource in Gemini API for large repo outlines / skeletons.
        Extends token lifespan and reduces prefill costs by up to 80%.
        """
        key = self._get_api_key()
        clean_model = model.replace("models/", "")
        endpoint = f"{self.base_url}/cachedContents?key={key}"

        payload: Dict[str, Any] = {
            "model": f"models/{clean_model}",
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": content}],
                }
            ],
            "ttl": f"{ttl_seconds}s",
        }
        if display_name:
            payload["displayName"] = display_name

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            raise ModelInferenceError(f"Gemini create_cached_content failed: {e}") from e
