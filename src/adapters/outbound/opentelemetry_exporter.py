import json
import time
from typing import Any, Dict, List

class OpenTelemetryExporter:
    """
    Exports token savings, latency, and agent execution spans in standard
    OpenTelemetry (OTel) ResourceSpans JSON format.
    """

    def __init__(self, service_name: str = "gravitational-singularity") -> None:
        self.service_name = service_name
        self._spans: List[Dict[str, Any]] = []

    def record_span(
        self,
        name: str,
        duration_ms: float,
        attributes: Dict[str, Any],
        status_code: str = "OK",
    ) -> None:
        now_ns = int(time.time() * 1_000_000_000)
        span = {
            "name": name,
            "start_time_unix_nano": now_ns - int(duration_ms * 1_000_000),
            "end_time_unix_nano": now_ns,
            "status": {"code": status_code},
            "attributes": [
                {"key": k, "value": {"string_value": str(v)}}
                for k, v in attributes.items()
            ],
        }
        self._spans.append(span)

    def export_otel_payload(self) -> Dict[str, Any]:
        return {
            "resource_spans": [
                {
                    "resource": {
                        "attributes": [
                            {"key": "service.name", "value": {"string_value": self.service_name}},
                            {"key": "service.version", "value": {"string_value": "0.2.0"}},
                        ]
                    },
                    "scope_spans": [
                        {
                            "scope": {"name": "singularity.token_factory"},
                            "spans": list(self._spans),
                        }
                    ],
                }
            ]
        }

    def export_jsonl(self) -> str:
        return "\n".join(json.dumps(s) for s in self._spans)
