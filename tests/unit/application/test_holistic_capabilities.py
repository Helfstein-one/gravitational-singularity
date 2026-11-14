import unittest
from src.application.dynamic_agent_governor import DynamicAgentGovernor
from src.application.hybrid_routing_engine import HybridRoutingEngine
from src.ports.inbound.hybrid_routing_port import ExecutionTier
from src.adapters.outbound.grammar_decoding_adapter import GrammarDecodingAdapter
from src.application.repo_map_pagerank_engine import RepoMapPageRankEngine
from src.application.hybrid_search_rrf import HybridSearchRRFEngine
from src.application.token_savings_estimator import TokenSavingsEstimator
from src.adapters.outbound.opentelemetry_exporter import OpenTelemetryExporter

class TestHolisticCapabilities(unittest.TestCase):

    def test_dynamic_agent_governor_strict_cap(self):
        # 8.5 GB Cap for 16GB Mac M4
        governor = DynamicAgentGovernor(vram_budget_cap_gb=8.5)

        # Activate small models
        self.assertTrue(governor.request_model_activation("smollm2:1.7b", 1.0))
        self.assertTrue(governor.request_model_activation("deepseek-r1:1.5b", 1.1))
        self.assertEqual(governor.current_vram_allocated_gb, 2.1)

        # Activate heavy 7B model (4.5 GB) -> Total 6.6 GB <= 8.5 GB
        self.assertTrue(governor.request_model_activation("qwen2.5-coder:7b", 4.5))
        self.assertEqual(governor.current_vram_allocated_gb, 6.6)

        # Activating another heavy model (4.5 GB) would exceed 8.5 GB -> Triggers LRU eviction
        self.assertTrue(governor.request_model_activation("qwen2.5-coder:3b", 3.0))
        # Total remains <= 8.5 GB
        self.assertLessEqual(governor.current_vram_allocated_gb, 8.5)

    def test_hybrid_routing_engine(self):
        router = HybridRoutingEngine()

        # Deterministic System 0
        dec1 = router.route_task("Format and organize imports in utils.py")
        self.assertEqual(dec1.tier, ExecutionTier.TIER_0_LOCAL_DETERMINISTIC)
        self.assertGreater(dec1.estimated_tokens_saved, 0)

        # Local Small Language Model
        dec2 = router.route_task("Implement helper function to calculate fibonacci", "def foo(): pass")
        self.assertEqual(dec2.tier, ExecutionTier.TIER_0_LOCAL_SLM)
        self.assertEqual(dec2.target_model, "qwen2.5-coder:7b")

        # Architectural Cloud Escalation
        dec3 = router.route_task("Refactor whole system cross-module architecture for microservices")
        self.assertEqual(dec3.tier, ExecutionTier.TIER_3_CLOUD_PRO)
        self.assertEqual(dec3.target_model, "gemini-2.0-pro")

    def test_grammar_decoding_adapter(self):
        adapter = GrammarDecodingAdapter()
        bnf = adapter.get_bnf_schema()
        self.assertIn("root ::=", bnf)

        # Clean JSON parsing
        raw_json = '{"node_id": "func_1", "symbol": "is_prime", "code": "def is_prime(n): return n > 1"}'
        parsed = adapter.parse_patch_output(raw_json)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed[1], "is_prime")

        # JSON embedded with conversational chatter
        noisy_output = "Sure! Here is the fix:\n" + raw_json + "\nHope this helps!"
        parsed_noisy = adapter.parse_patch_output(noisy_output)
        self.assertIsNotNone(parsed_noisy)
        self.assertEqual(parsed_noisy[0], "func_1")

    def test_repo_map_pagerank_engine(self):
        engine = RepoMapPageRankEngine()
        files = {
            "app.py": "from service import DataService\ndef main(): DataService().run()",
            "service.py": "from db import Database\nclass DataService:\n    def run(self): pass",
            "db.py": "class Database:\n    def query(self): pass",
        }

        # Active file is app.py -> should bias ranking
        repo_map = engine.build_repo_map(files, active_file="app.py", max_tokens=200)
        self.assertIn("Repository Structural Map", repo_map)
        self.assertIn("DataService", repo_map)
        # Token budget length check
        self.assertLessEqual(len(repo_map), 200 * 5)

    def test_hybrid_search_rrf_engine(self):
        engine = HybridSearchRRFEngine(rrf_k=60)
        engine.index_document("doc1", "def authenticate_user(token: str): pass")
        engine.index_document("doc2", "def query_database(sql: str): pass")

        results = engine.search("authenticate user token", top_k=2)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0].document_id, "doc1")
        self.assertGreater(results[0].rrf_score, 0.0)

    def test_token_savings_estimator(self):
        estimator = TokenSavingsEstimator()
        estimator.record_compression_event("ast-skeletonizer", 5000, 1500)
        estimator.record_compression_event("in-memory-guardrail", 10000, 0)

        report = estimator.get_summary_report()
        self.assertEqual(report.raw_tokens_projected, 15000)
        self.assertEqual(report.tokens_saved_total, 13500)
        self.assertGreater(report.cost_avoided_usd, 0.0)

        # Dynamic tier recommendations
        self.assertEqual(TokenSavingsEstimator.recommend_gemini_tier(500), "gemini-2.0-flash-lite")
        self.assertEqual(TokenSavingsEstimator.recommend_gemini_tier(10_000), "gemini-2.0-flash")
        self.assertEqual(TokenSavingsEstimator.recommend_gemini_tier(50_000, is_architectural=True), "gemini-2.0-pro")

    def test_opentelemetry_exporter(self):
        exporter = OpenTelemetryExporter()
        exporter.record_span("token_compression", 12.5, {"tokens_saved": 3500, "tier": "tier_0"})
        payload = exporter.export_otel_payload()
        self.assertEqual(payload["resource_spans"][0]["resource"]["attributes"][0]["value"]["string_value"], "gravitational-singularity")
        self.assertEqual(len(payload["resource_spans"][0]["scope_spans"][0]["spans"]), 1)

if __name__ == "__main__":
    unittest.main()
