"""
Outbound Adapter: L4 Semantic Knowledge Graph Adapter (SQLite WAL).
Compiles cross-session architectural decisions, design invariants, and contracts
into an embedded knowledge graph (knowledge_graph.sqlite).
Zero external dependencies (Python standard library only).
"""

from __future__ import annotations
import json
import os
import sqlite3
import time
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass(frozen=True)
class ArchitecturalDecision:
    id: str
    title: str
    context: str
    decision: str
    rationale: str
    tags: List[str]
    created_at: float


class SqliteKnowledgeGraphAdapter:
    """
    Persistent L4 Knowledge Graph storing immutable architectural contracts.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or os.path.expanduser("~/.gemini/config/cache/knowledge_graph.sqlite")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS architectural_decisions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    context TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    created_at REAL NOT NULL
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_decisions_title ON architectural_decisions (title);")

    def record_decision(
        self,
        decision_id: str,
        title: str,
        context: str,
        decision: str,
        rationale: str,
        tags: Optional[List[str]] = None,
    ) -> ArchitecturalDecision:
        now = time.time()
        tags_list = tags or []
        record = ArchitecturalDecision(
            id=decision_id,
            title=title,
            context=context,
            decision=decision,
            rationale=rationale,
            tags=tags_list,
            created_at=now,
        )
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO architectural_decisions
                (id, title, context, decision, rationale, tags_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (record.id, record.title, record.context, record.decision, record.rationale, json.dumps(record.tags), record.created_at),
            )
        return record

    def query_decisions(self, tag: Optional[str] = None, keyword: Optional[str] = None) -> List[ArchitecturalDecision]:
        query = "SELECT id, title, context, decision, rationale, tags_json, created_at FROM architectural_decisions"
        params: List[Any] = []
        clauses: List[str] = []

        if keyword:
            clauses.append("(title LIKE ? OR context LIKE ? OR decision LIKE ?)")
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw])
        if tag:
            clauses.append("tags_json LIKE ?")
            params.append(f"%{tag}%")

        if clauses:
            query += " WHERE " + " AND ".join(clauses)

        query += " ORDER BY created_at DESC;"

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()

        results: List[ArchitecturalDecision] = []
        for r in rows:
            results.append(
                ArchitecturalDecision(
                    id=r[0],
                    title=r[1],
                    context=r[2],
                    decision=r[3],
                    rationale=r[4],
                    tags=json.loads(r[5]) if r[5] else [],
                    created_at=r[6],
                )
            )
        return results
