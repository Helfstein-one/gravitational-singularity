"""
Outbound Adapter: Ollama HTTP API Adapter.
Implements ILLMClient using Python standard library urllib.
"""

from __future__ import annotations
import json
import urllib.request
import urllib.error
from typing import Any
from src.ports.outbound.llm_client_port import ILLMClient
from src.domain.exceptions import ModelInferenceError


class OllamaClientAdapter(ILLMClient):
    """Concrete implementation of ILLMClient for local Ollama daemon."""

    def __init__(self, base_url: str = "http://127.0.0.1:11434"):
        self.base_url = base_url.rstrip("/")

    def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        response_format: str | dict[str, Any] | None = None,
        grammar: str | None = None,
    ) -> str:
        # Zero cold-swap (keep_alive: -1) and KV-cache prefill preservation (num_keep)
        options: dict[str, Any] = {
            "temperature": temperature,
            "keep_alive": -1,
            "f16_kv": True,
        }
        if grammar:
            options["grammar"] = grammar

        if system_prompt:
            num_keep = max(32, int(len(system_prompt) / 3.8))
            options["num_keep"] = num_keep

        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": -1,
            "options": options,
        }
        if system_prompt:
            payload["system"] = system_prompt
        if response_format:
            payload["format"] = response_format

        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response", "")
        except Exception as e:
            raise ModelInferenceError(f"Ollama generation failed for {model}: {e}") from e

    def embed(self, text: str, model: str = "nomic-embed-text") -> list[float]:
        payload = {"model": model, "prompt": text}
        req = urllib.request.Request(
            f"{self.base_url}/api/embeddings",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("embedding", [])
        except Exception as e:
            raise ModelInferenceError(f"Ollama embedding failed for {model}: {e}") from e

    def list_models(self) -> list[dict[str, Any]]:
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = []
                for m in data.get("models", []):
                    name = m.get("name", "")
                    sz = round(m.get("size", 0) / (1024**3), 2)
                    role = "General"
                    if "coder" in name or "-c" in name:
                        role = "Builder / Coding"
                    elif "smollm" in name:
                        role = "Micro-Worker / Fast Coder"
                    elif "hermes" in name or "moe" in name:
                        role = "Agentic / Tool Calling"
                    elif "deepseek-r1" in name or "-r" in name:
                        role = "Skeptic / Reasoning"
                    elif "embed" in name:
                        role = "Scout / Semantic RAG"
                    models.append({"name": name, "size_gb": sz, "role": role})
                return models
        except Exception:
            return []

    def lock_models_in_vram(self, models: list[str]) -> dict[str, bool]:
        """Locks model weights in Apple Silicon Metal VRAM with keep_alive: -1, preventing macOS paging."""
        results: dict[str, bool] = {}
        for m in models:
            payload = {
                "model": m,
                "prompt": "",
                "keep_alive": -1,
            }
            try:
                req = urllib.request.Request(
                    f"{self.base_url}/api/generate",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    results[m] = resp.status == 200
            except Exception:
                results[m] = False
        return results
