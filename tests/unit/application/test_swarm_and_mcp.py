import json
import unittest
from src.application.swarm_orchestrator import SwarmOrchestrator
from src.adapters.inbound.universal_mcp_server import UniversalMCPServer

class TestSwarmAndUniversalMCP(unittest.TestCase):

    def test_swarm_planning_and_execution(self):
        orchestrator = SwarmOrchestrator()
        files = {
            "main.py": "from auth import login\ndef run(): login('admin')",
            "auth.py": "def login(user): return user == 'admin'",
        }

        # Plan swarm execution
        plan = orchestrator.plan_swarm_execution("Refactor login verification", files, active_file="main.py")
        self.assertIn("shared_repo_map", plan)
        self.assertTrue(len(plan["tasks"]) >= 2)

        # Execute swarm tasks
        results = orchestrator.execute_swarm(plan["tasks"])
        self.assertEqual(len(results), len(plan["tasks"]))
        for r in results:
            self.assertEqual(r.status, "SUCCESS")
            self.assertIn(r.role.upper(), r.output)

    def test_universal_mcp_json_rpc(self):
        server = UniversalMCPServer()

        # Test tools/list
        req_list = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        resp_list = json.loads(server.handle_json_rpc(req_list))
        self.assertEqual(resp_list["id"], 1)
        self.assertTrue("tools" in resp_list["result"])

        # Test tools/call: compress_ast
        req_call = json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "compress_ast",
                "arguments": {"code": "def long_func():\n    x = 1\n    y = 2\n    return x + y"},
            },
        })
        resp_call = json.loads(server.handle_json_rpc(req_call))
        self.assertEqual(resp_call["id"], 2)
        content = json.loads(resp_call["result"]["content"][0]["text"])
        self.assertIn("def long_func", content["compressed_code"])

        # Test tools/call: get_vram_status
        req_vram = json.dumps({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "get_vram_status", "arguments": {}},
        })
        resp_vram = json.loads(server.handle_json_rpc(req_vram))
        vram_data = json.loads(resp_vram["result"]["content"][0]["text"])
        self.assertEqual(vram_data["vram_budget_cap_gb"], 8.5)

if __name__ == "__main__":
    unittest.main()
