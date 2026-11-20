"""
Integration & Unit Tests for GeminiClientAdapter and UniversalMCPServer Cloud Tiering.
Tests zero-dependency HTTP communication via standard library mocking.
"""

import io
import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from src.adapters.outbound.gemini_client_adapter import GeminiClientAdapter
from src.adapters.inbound.universal_mcp_server import UniversalMCPServer
from src.domain.exceptions import ModelInferenceError


class TestGeminiClientAdapter(unittest.TestCase):

    def setUp(self):
        self.adapter = GeminiClientAdapter(api_key="test-gemini-key")

    def test_missing_api_key_raises_error(self):
        adapter_no_key = GeminiClientAdapter(api_key="")
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ModelInferenceError) as ctx:
                adapter_no_key.generate("Hello", model="gemini-2.5-flash")
            self.assertIn("API key is not configured", str(ctx.exception))

    @patch("urllib.request.urlopen")
    def test_generate_standard_text_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "Surgical patch successfully generated."}]
                    }
                }
            ]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = self.adapter.generate(
            prompt="Refactor method X",
            model="gemini-2.5-flash",
            system_prompt="You are an expert compiler.",
            temperature=0.2,
        )

        self.assertEqual(res, "Surgical patch successfully generated.")
        self.assertTrue(mock_urlopen.called)
        req = mock_urlopen.call_args[0][0]
        self.assertIn("gemini-2.5-flash:generateContent", req.full_url)
        self.assertIn("key=test-gemini-key", req.full_url)

        sent_payload = json.loads(req.data.decode("utf-8"))
        self.assertIn("systemInstruction", sent_payload)
        self.assertEqual(sent_payload["generationConfig"]["temperature"], 0.2)

    @patch("urllib.request.urlopen")
    def test_generate_with_thinking_budget(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"thought": "Analyzing race condition..."},
                            {"text": "Resolved concurrency deadlock."}
                        ]
                    }
                }
            ]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = self.adapter.generate(
            prompt="Debug concurrency invariant",
            model="gemini-2.0-flash-thinking-exp",
            thinking_budget=2048,
        )

        self.assertEqual(res, "Resolved concurrency deadlock.")
        req = mock_urlopen.call_args[0][0]
        sent_payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(sent_payload["generationConfig"]["thinkingConfig"]["thinkingBudget"], 2048)

    @patch("urllib.request.urlopen")
    def test_generate_with_structured_json_schema(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": '{"TargetContent": "old", "ReplacementContent": "new"}'}]
                    }
                }
            ]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        schema = {
            "type": "object",
            "properties": {
                "TargetContent": {"type": "string"},
                "ReplacementContent": {"type": "string"},
            },
            "required": ["TargetContent", "ReplacementContent"],
        }

        res = self.adapter.generate(
            prompt="Replace foo with bar",
            model="gemini-2.5-pro",
            response_format=schema,
        )

        self.assertIn('"TargetContent": "old"', res)
        req = mock_urlopen.call_args[0][0]
        sent_payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(sent_payload["generationConfig"]["responseMimeType"], "application/json")
        self.assertEqual(sent_payload["generationConfig"]["responseSchema"], schema)

    @patch("urllib.request.urlopen")
    def test_embed_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "embedding": {
                "values": [0.12, -0.34, 0.56, 0.78]
            }
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        vec = self.adapter.embed("semantic search vector", model="text-embedding-004")
        self.assertEqual(vec, [0.12, -0.34, 0.56, 0.78])
        req = mock_urlopen.call_args[0][0]
        self.assertIn("text-embedding-004:embedContent", req.full_url)

    @patch("urllib.request.urlopen")
    def test_create_cached_content(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "name": "cachedContents/repo-map-123",
            "expireTime": "2026-11-20T21:00:00Z",
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        cache = self.adapter.create_cached_content(
            content="class LargeRepoMap: ...",
            model="gemini-2.5-pro",
            ttl_seconds=1800,
            display_name="repo_map_cache",
        )

        self.assertEqual(cache["name"], "cachedContents/repo-map-123")
        req = mock_urlopen.call_args[0][0]
        self.assertIn("cachedContents", req.full_url)
        sent_payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(sent_payload["ttl"], "1800s")
        self.assertEqual(sent_payload["displayName"], "repo_map_cache")

    @patch("urllib.request.urlopen")
    def test_http_error_handling(self, mock_urlopen):
        err = HTTPError(
            url="https://generativelanguage.googleapis.com",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=io.BytesIO(b'{"error": {"message": "Resource exhausted"}}'),
        )
        mock_urlopen.side_effect = err

        with self.assertRaises(ModelInferenceError) as ctx:
            self.adapter.generate("Test prompt", model="gemini-2.5-flash")
        self.assertIn("HTTP 429", str(ctx.exception))


class TestUniversalMCPServerGeminiIntegration(unittest.TestCase):

    def setUp(self):
        self.mock_gemini = MagicMock(spec=GeminiClientAdapter)
        self.server = UniversalMCPServer(gemini_client=self.mock_gemini)

    def test_execute_gemini_tier_mcp_tool_success(self):
        self.mock_gemini.generate.return_value = "Cloud solution generated"

        call_args = {
            "prompt": "Design multi-region architecture",
            "model": "gemini-2.5-pro",
            "thinking_budget": 4096,
        }

        result = self.server.dispatch_call("execute_gemini_tier", call_args)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["model"], "gemini-2.5-pro")
        self.assertEqual(result["response"], "Cloud solution generated")
        self.assertEqual(result["thinking_budget"], 4096)

        self.mock_gemini.generate.assert_called_once_with(
            prompt="Design multi-region architecture",
            model="gemini-2.5-pro",
            system_prompt=None,
            thinking_budget=4096,
        )

    def test_mcp_tools_list_contains_gemini_tier(self):
        defs = self.server.get_tool_definitions()
        tool_names = [t["name"] for t in defs["tools"]]
        self.assertIn("execute_gemini_tier", tool_names)
        self.assertIn("compress_ast", tool_names)
        self.assertIn("route_task", tool_names)


if __name__ == "__main__":
    unittest.main()
