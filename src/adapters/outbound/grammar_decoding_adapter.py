import json
import re
from typing import Any, Dict, Optional, Tuple

class GrammarDecodingAdapter:
    """
    Constrained BNF Grammar decoder ensuring local LLMs output strictly
    canonical symbolic patch tuples without conversational padding.
    """

    BNF_GRAMMAR_SCHEMA = """
    root ::= Patch
    Patch ::= "{" ws "\\"node_id\\":" ws String "," ws "\\"symbol\\":" ws String "," ws "\\"code\\":" ws String ws "}"
    String ::= "\\"" [^"\\\\]* "\\""
    ws ::= [ \\t\\n\\r]*
    """

    @classmethod
    def get_bnf_schema(cls) -> str:
        return cls.BNF_GRAMMAR_SCHEMA.strip()

    @classmethod
    def get_json_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "node_id": {"type": "string"},
                "symbol": {"type": "string"},
                "code": {"type": "string"},
            },
            "required": ["node_id", "symbol", "code"],
        }

    @classmethod
    def parse_patch_output(cls, raw_output: str) -> Optional[Tuple[str, str, str]]:
        """Extracts (node_id, symbol, code) from constrained output, rejecting unconstrained chatter."""
        clean_text = raw_output.strip()

        # Try parsing directly as JSON
        try:
            data = json.loads(clean_text)
            if "node_id" in data and "symbol" in data and "code" in data:
                return data["node_id"], data["symbol"], data["code"]
        except Exception:
            pass

        # Try extracting JSON object substring
        json_match = re.search(r"\{[^{}]*\"node_id\"[^{}]*\}", clean_text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                return data.get("node_id", ""), data.get("symbol", ""), data.get("code", "")
            except Exception:
                pass

        # Try tuple notation (NODE_ID, SYMBOL, CODE)
        tuple_match = re.search(r"\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*,\s*['\"](.*)['\"]\s*\)", clean_text, re.DOTALL)
        if tuple_match:
            return tuple_match.group(1), tuple_match.group(2), tuple_match.group(3)

        return None
