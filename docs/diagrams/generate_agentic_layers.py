#!/usr/bin/env python3
"""
Generates the "Agentic Action Layers" diagram from a single layout definition:
  - docs/diagrams/agentic_layers.drawio  (editable in app.diagrams.net / VS Code Draw.io)
  - assets/agentic_layers.svg            (rendered image embedded in README.md)

Standard library only. Run from repo root:
    python3 docs/diagrams/generate_agentic_layers.py
"""

from __future__ import annotations
import os
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DRAWIO_OUT = os.path.join(ROOT, "docs", "diagrams", "agentic_layers.drawio")
SVG_OUT = os.path.join(ROOT, "assets", "agentic_layers.svg")

W, H = 1600, 1260
BG = "#0d1117"
LAYER_FILL = "#161b22"
BOX_FILL = "#1c2128"
TEXT = "#e6edf3"
MUTED = "#8b949e"
ACTIVE = "#3fb950"
LIBRARY = "#d29922"

# ---------------------------------------------------------------------------
# Layout definition
# ---------------------------------------------------------------------------
LAYERS = [
    # id, y, h, title, color
    ("L1", 100, 120, "CAMADA 1 · ENTRADA & ORQUESTRAÇÃO (Cloud)", "#58a6ff"),
    ("L2", 240, 160, "CAMADA 2 · INTERCEPTAÇÃO PreToolUse (antes de executar/escrever)", "#f85149"),
    ("L3", 420, 150, "CAMADA 3 · ROTEAMENTO COGNITIVO (Sistema 1 vs Sistema 2)", "#a371f7"),
    ("L4", 590, 170, "CAMADA 4 · EXECUÇÃO LOCAL TIER 0 (custo de nuvem $0)", "#3fb950"),
    ("L5", 780, 160, "CAMADA 5 · MEMÓRIA & CONTEXTO", "#39c5cf"),
    ("L6", 960, 200, "CAMADA 6 · MODELOS LOCAIS & HARDWARE (Apple Silicon 16 GB · Metal GPU)", "#f0883e"),
]

# id, layer_color, x, y, w, h, title, lines, status ('active' | 'library' | 'plain')
BOXES = [
    # L1
    ("dev", "#58a6ff", 90, 130, 230, 76, "Desenvolvedor",
     ["Prompt em linguagem natural", "/grill-me · /plan · pedidos de edição"], "active"),
    ("ide", "#58a6ff", 350, 130, 500, 76, "Antigravity IDE · Agente Orquestrador",
     ["Planeja e emite tool calls: edit_file, run_command, view_file, MCP",
      "Segue AGENTS.md (Event Horizon: patches cirúrgicos, brevidade)"], "active"),
    ("cloud", "#58a6ff", 880, 130, 330, 76, "Tiers de modelo na nuvem",
     ["pro: arquitetura e decisões críticas",
      "flash: pesquisa ampla · flash_lite: lint/lookups"], "active"),
    # L2
    ("hook", "#f85149", 90, 272, 250, 114, "hook_pre_tool.py",
     ["Recebe a tool call (JSON via stdin)", "→ hook_adapter.run_hook()",
      "Falha segura: payload inválido = allow", "Executa em toda tool call"], "active"),
    ("guard", "#f85149", 370, 272, 510, 114, "GuardrailInterceptor.evaluate()",
     ["1. Comando destrutivo → deny",
      "2. view_file sem fatia em arquivo longo → deny",
      "3. Patch aplicado em RAM + ast.parse → deny se sintaxe quebrar",
      "4. Testes → prefixa test-slicer · comandos verbosos → prefixa rtk"], "active"),
    ("decision", "#f85149", 910, 272, 300, 114, "Decisão devolvida ao IDE",
     ["allow → tool executa normalmente", "deny → motivo + linha do erro",
      "overwrite → CommandLine reescrita", "(nada toca o disco antes disso)"], "active"),
    # L3
    ("arbiter", "#a371f7", 90, 452, 360, 102, "CognitiveArbiter",
     ["Classifica a tarefa por heurística (<2 ms)",
      "Sistema 1: local, rápido · Sistema 2: nuvem",
      "Calcula envelope de orçamento de tokens"], "library"),
    ("breaker", "#a371f7", 470, 452, 360, 102, "EscalationCircuitBreaker",
     ["1ª falha local → permite 1 retry",
      "2ª falha → abre o circuito",
      "Gera handoff cirúrgico para a nuvem"], "library"),
    ("squeezer", "#a371f7", 850, 452, 360, 102, "EpistemicContextSqueezer",
     ["Poda virtual do histórico (teto 8k tokens)",
      "Preserva input do usuário + 2 turnos recentes",
      "Não-destrutivo: projeção em memória"], "library"),
    # L4
    ("mcp", "#3fb950", 90, 622, 360, 122, "local-llm-mcp (mcp_adapter.py)",
     ["Chamado pelo IDE via MCP stdio (JSON-RPC)",
      "query_local_llm · local_extract_json",
      "local_format_code · local_semantic_search",
      "local_draft_patch"], "active"),
    ("drafter", "#3fb950", 470, 622, 260, 122, "SpeculativeDrafter",
     ["+ SemanticRetriever",
      "Draft no qwen 7B + validação AST",
      "1 retry de auto-correção",
      "RAG: chunks AST + nomic-embed"], "active"),
    ("cascade", "#3fb950", 750, 622, 225, 122, "HierarchicalCascade",
     ["Micro-tarefa → smollm2 1.7B",
      "AST inválida → promove p/ 7B",
      "Estrutural → direto no 7B"], "library"),
    ("reflector", "#3fb950", 990, 622, 220, 122, "AdversarialReflector",
     ["Builder (qwen 7B) gera",
      "Skeptic (r1 1.5B) critica",
      "No máx. 1 rodada de refino"], "library"),
    # L5
    ("prewarmer", "#39c5cf", 90, 812, 260, 112, "PredictivePreWarmer",
     ["Thread dentro do daemon :7890",
      "Varre src/ e tests/ (mtime + size)",
      "Debounce 300 ms → pré-esqueletiza"], "active"),
    ("memoizer", "#39c5cf", 370, 812, 270, 112, "EpistemicMemoizer",
     ["+ CodeSkeletonizer",
      "Chave: sha256(conteúdo) + prompt + tool",
      "Esqueleto AST ≈ 68% menos tokens"], "active"),
    ("sqlite", "#39c5cf", 670, 812, 250, 112, "Cache Epistêmico L1 / L2",
     ["L1: LRU em RAM (500 entradas)",
      "L2: SQLite WAL em disco",
      "~/.gemini/config/cache/epistemic.db"], "active"),
    ("merkle", "#39c5cf", 940, 812, 270, 112, "AstMerkleEngine",
     ["Um nó por símbolo, hash SHA-256",
      "Re-esqueletiza só o nó alterado",
      "Persiste em ast_merkle_nodes (L2)"], "library"),
    # L6
    ("optimizer", "#f0883e", 90, 992, 280, 150, "InferenceOptimizer",
     ["Boot do daemon: warmup_async()",
      "keep_alive = -1 nos 3 modelos núcleo",
      "OllamaAdapter injeta num_keep",
      "(≈ tokens do system prompt)",
      "Orçamento VRAM alvo: ≤ 7 GB"], "active"),
    ("ollama", "#f0883e", 420, 992, 250, 150, "Ollama :11434",
     ["/api/generate", "/api/embeddings", "/api/ps (inspeção de VRAM)",
      "Metal GPU · memória unificada"], "active"),
    ("m_smol", "#f0883e", 700, 992, 160, 66, "smollm2:1.7b", ["Micro-worker · ~1.0 GB"], "plain"),
    ("m_r1", "#f0883e", 875, 992, 160, 66, "deepseek-r1:1.5b", ["Skeptic · ~1.1 GB"], "plain"),
    ("m_qwen", "#f0883e", 1050, 992, 160, 66, "qwen2.5-coder:7b", ["Builder · ~4.7 GB"], "plain"),
    ("m_embed", "#f0883e", 700, 1074, 245, 66, "nomic-embed-text", ["Scout / RAG · ~0.27 GB"], "plain"),
    ("m_hermes", "#f0883e", 965, 1074, 245, 66, "hermes3:3b", ["Distiller de sessão · ~2.0 GB"], "plain"),
    # Right column
    ("telemetry", "#58a6ff", 1270, 420, 290, 360, "Daemon de Telemetria :7890",
     ["http_telemetry_adapter (start/stop/restart)",
      "No boot inicia: PreWarmer + warmup VRAM",
      "GET /api/stats · dashboard web",
      "",
      "Métricas calculadas de dados reais:",
      "· tokens, custo, economia (transcripts)",
      "· epistemic_cache (contagem no SQLite)",
      "· predictive_prewarm (thread ativa)",
      "",
      "Valores fixos / ilustrativos hoje:",
      "· cascade_metrics",
      "· merkle_tree_metrics",
      "· vram_coresidence_metrics",
      "· adversarial_reflection_metrics",
      "· context_squeeze_metrics",
      "",
      "Tornam-se reais quando os módulos",
      "da camada 3/4/5 forem conectados."], "active"),
    ("flow", "#58a6ff", 1270, 800, 290, 240, "Fluxo típico de uma edição",
     ["① Dev descreve a mudança",
      "② IDE planeja e (opcional) consulta",
      "\u00a0\u00a0\u00a0\u00a0\u00a0o MCP local para RAG / draft",
      "③ Draft local: qwen 7B + AST check",
      "④ IDE emite edit_file / run_command",
      "⑤ Hook valida em RAM: allow/deny",
      "⑥ Só então o disco é alterado",
      "⑦ PreWarmer vê o mtime novo e",
      "\u00a0\u00a0\u00a0\u00a0\u00a0re-esqueletiza para o cache",
      "⑧ Próxima leitura sai do cache L1"], "plain"),
]

# Arrows: (points, label, label_xy, dashed, color)
ARROWS = [
    ([(320, 168), (350, 168)], "", None, False, TEXT),
    ([(420, 206), (420, 230), (76, 230), (76, 329), (90, 329)], "toda tool call", (430, 244), False, "#f85149"),
    ([(340, 329), (370, 329)], "", None, False, "#f85149"),
    ([(880, 329), (910, 329)], "", None, False, "#f85149"),
    ([(1060, 272), (1060, 234), (800, 234), (800, 206)], "allow · deny · overwrite", (1068, 262), False, "#f85149"),
    ([(380, 206), (380, 214), (58, 214), (58, 683), (90, 683)], "", None, False, ACTIVE),
    ([(450, 683), (470, 683)], "", None, False, ACTIVE),
    ([(655, 744), (655, 992)], "generate / embed", (662, 954), False, ACTIVE),
    ([(350, 868), (370, 868)], "", None, False, "#39c5cf"),
    ([(640, 868), (670, 868)], "", None, False, "#39c5cf"),
    ([(940, 868), (920, 868)], "", None, True, LIBRARY),
    ([(930, 744), (930, 972), (780, 972), (780, 992)], "", None, True, LIBRARY),
    ([(370, 1067), (420, 1067)], "warmup", (373, 1058), False, "#f0883e"),
    ([(670, 1067), (700, 1067)], "", None, False, "#f0883e"),
]


# ---------------------------------------------------------------------------
# SVG rendering
# ---------------------------------------------------------------------------
def _svg() -> str:
    out: list[str] = []
    a = out.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'xml:space="preserve" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif">')
    a("<defs>")
    for name, color in [("t", TEXT), ("r", "#f85149"), ("g", ACTIVE), ("c", "#39c5cf"),
                        ("o", "#f0883e"), ("y", LIBRARY)]:
        a(f'<marker id="m{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
          f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>')
    a("</defs>")
    a(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    a(f'<text x="{W/2}" y="48" text-anchor="middle" font-size="26" font-weight="700" fill="#58a6ff">'
      f'EVENT HORIZON · CAMADAS DE AÇÃO AGÊNTICA</text>')
    a(f'<text x="{W/2}" y="76" text-anchor="middle" font-size="14" fill="{MUTED}">'
      f'Do prompt ao disco: orquestração na nuvem, interceptação em RAM, execução local Tier 0, '
      f'memória epistêmica e modelos residentes no Apple Silicon</text>')

    for _id, y, h, title, color in LAYERS:
        a(f'<rect x="40" y="{y}" width="1200" height="{h}" rx="10" fill="{LAYER_FILL}" '
          f'stroke="{color}" stroke-width="1.5" stroke-opacity="0.8"/>')
        a(f'<text x="96" y="{y + 20}" font-size="13" font-weight="700" fill="{color}" '
          f'letter-spacing="0.5">{escape(title)}</text>')

    for _id, color, x, y, w, h, title, lines, status in BOXES:
        stroke = {"active": ACTIVE, "library": LIBRARY}.get(status, color)
        dash = ' stroke-dasharray="7 5"' if status == "library" else ""
        a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{BOX_FILL}" '
          f'stroke="{stroke}" stroke-width="2"{dash}/>')
        a(f'<text x="{x + 12}" y="{y + 21}" font-size="14" font-weight="700" fill="{color}">'
          f'{escape(title)}</text>')
        if status in ("active", "library"):
            tag = "● ATIVO" if status == "active" else "○ BIBLIOTECA"
            a(f'<text x="{x + w - 10}" y="{y + h - 9}" text-anchor="end" font-size="10" '
              f'font-weight="700" fill="{stroke}">{tag}</text>')
        for i, line in enumerate(lines):
            a(f'<text x="{x + 12}" y="{y + 41 + i * 17}" font-size="12" fill="{TEXT}">'
              f'{escape(line)}</text>')

    marker_for = {TEXT: "mt", "#f85149": "mr", ACTIVE: "mg", "#39c5cf": "mc",
                  "#f0883e": "mo", LIBRARY: "my"}
    for pts, label, lxy, dashed, color in ARROWS:
        d = " ".join(f"{px},{py}" for px, py in pts)
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        a(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="2"{dash} '
          f'marker-end="url(#{marker_for[color]})"/>')
        if label and lxy:
            a(f'<text x="{lxy[0]}" y="{lxy[1]}" font-size="11" font-style="italic" fill="{color}">'
              f'{escape(label)}</text>')

    a(f'<text x="52" y="600" transform="rotate(-90 52 600)" text-anchor="middle" font-size="11" '
      f'font-style="italic" fill="{ACTIVE}">MCP stdio (JSON-RPC)</text>')

    # Legend
    lx, ly = 1270, 100
    a(f'<rect x="{lx}" y="{ly}" width="290" height="300" rx="10" fill="{LAYER_FILL}" stroke="{MUTED}"/>')
    a(f'<text x="{lx + 14}" y="{ly + 26}" font-size="14" font-weight="700" fill="{TEXT}">LEGENDA</text>')
    a(f'<rect x="{lx + 14}" y="{ly + 44}" width="40" height="22" rx="5" fill="{BOX_FILL}" stroke="{ACTIVE}" stroke-width="2"/>')
    a(f'<text x="{lx + 64}" y="{ly + 54}" font-size="12" fill="{TEXT}">ATIVO: conectado em runtime</text>')
    a(f'<text x="{lx + 64}" y="{ly + 69}" font-size="11" fill="{MUTED}">via hook, MCP ou daemon</text>')
    a(f'<rect x="{lx + 14}" y="{ly + 88}" width="40" height="22" rx="5" fill="{BOX_FILL}" stroke="{LIBRARY}" stroke-width="2" stroke-dasharray="7 5"/>')
    a(f'<text x="{lx + 64}" y="{ly + 98}" font-size="12" fill="{TEXT}">BIBLIOTECA: implementado</text>')
    a(f'<text x="{lx + 64}" y="{ly + 113}" font-size="11" fill="{MUTED}">e testado, sem adaptador</text>')
    a(f'<text x="{lx + 64}" y="{ly + 127}" font-size="11" fill="{MUTED}">que o chame ainda</text>')
    a(f'<line x1="{lx + 14}" y1="{ly + 152}" x2="{lx + 54}" y2="{ly + 152}" stroke="{TEXT}" stroke-width="2" marker-end="url(#mt)"/>')
    a(f'<text x="{lx + 64}" y="{ly + 156}" font-size="12" fill="{TEXT}">fluxo real de dados</text>')
    a(f'<line x1="{lx + 14}" y1="{ly + 180}" x2="{lx + 54}" y2="{ly + 180}" stroke="{LIBRARY}" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#my)"/>')
    a(f'<text x="{lx + 64}" y="{ly + 184}" font-size="12" fill="{TEXT}">fluxo previsto (não ligado)</text>')
    a(f'<text x="{lx + 14}" y="{ly + 216}" font-size="11" fill="{MUTED}">Zero dependências externas:</text>')
    a(f'<text x="{lx + 14}" y="{ly + 232}" font-size="11" fill="{MUTED}">somente Python stdlib 3.10+</text>')
    a(f'<text x="{lx + 14}" y="{ly + 256}" font-size="11" fill="{MUTED}">Arquitetura hexagonal:</text>')
    a(f'<text x="{lx + 14}" y="{ly + 272}" font-size="11" fill="{MUTED}">domain → ports → application</text>')
    a(f'<text x="{lx + 14}" y="{ly + 288}" font-size="11" fill="{MUTED}">→ adapters (inbound / outbound)</text>')

    a(f'<text x="40" y="{H - 40}" font-size="12" fill="{MUTED}">Fonte editável: docs/diagrams/agentic_layers.drawio · '
      f'gerado por docs/diagrams/generate_agentic_layers.py</text>')
    a("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# draw.io rendering
# ---------------------------------------------------------------------------
def _attr(s: str) -> str:
    return escape(s, {'"': "&quot;"})


def _drawio() -> str:
    cells: list[str] = []
    c = cells.append
    n = 0

    def nid() -> str:
        nonlocal n
        n += 1
        return f"c{n}"

    def text(x, y, w, h, html, size, color, bold=False, align="center"):
        style = (f"text;html=1;strokeColor=none;fillColor=none;align={align};verticalAlign=middle;"
                 f"whiteSpace=wrap;fontSize={size};fontColor={color};fontStyle={1 if bold else 0};")
        c(f'<mxCell id="{nid()}" value="{_attr(html)}" style="{style}" vertex="1" parent="1">'
          f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')

    text(200, 28, 1200, 34, "EVENT HORIZON · CAMADAS DE AÇÃO AGÊNTICA", 26, "#58a6ff", True)
    text(150, 64, 1300, 22, "Do prompt ao disco: orquestração na nuvem, interceptação em RAM, execução local "
         "Tier 0, memória epistêmica e modelos residentes no Apple Silicon", 14, MUTED)

    for _id, y, h, title, color in LAYERS:
        style = (f"rounded=1;arcSize=3;whiteSpace=wrap;html=1;fillColor={LAYER_FILL};strokeColor={color};"
                 f"fontColor={color};fontStyle=1;fontSize=13;align=left;verticalAlign=top;spacingLeft=54;spacingTop=2;")
        c(f'<mxCell id="{_id}" value="{_attr(escape(title))}" style="{style}" vertex="1" parent="1">'
          f'<mxGeometry x="40" y="{y}" width="1200" height="{h}" as="geometry"/></mxCell>')

    for _id, color, x, y, w, h, title, lines, status in BOXES:
        stroke = {"active": ACTIVE, "library": LIBRARY}.get(status, color)
        dashed = "dashed=1;dashPattern=7 5;" if status == "library" else ""
        tag = {"active": " <font color='%s' style='font-size:10px'>● ATIVO</font>" % ACTIVE,
               "library": " <font color='%s' style='font-size:10px'>○ BIBLIOTECA</font>" % LIBRARY}.get(status, "")
        body = "<br>".join(escape(l) if l else "&nbsp;" for l in lines)
        html = (f"<b><font color='{color}' style='font-size:14px'>{escape(title)}</font></b>{tag}"
                f"<br><font color='{TEXT}' style='font-size:12px'>{body}</font>")
        style = (f"rounded=1;arcSize=6;whiteSpace=wrap;html=1;fillColor={BOX_FILL};strokeColor={stroke};"
                 f"strokeWidth=2;{dashed}align=left;verticalAlign=top;spacingLeft=10;spacingTop=4;")
        c(f'<mxCell id="{_id}" value="{_attr(html)}" style="{style}" vertex="1" parent="1">'
          f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')

    for pts, label, _lxy, dashed, color in ARROWS:
        (sx, sy), (tx, ty) = pts[0], pts[-1]
        mids = "".join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in pts[1:-1])
        style = (f"endArrow=block;endFill=1;html=1;strokeWidth=2;strokeColor={color};fontColor={color};"
                 f"fontStyle=2;fontSize=11;labelBackgroundColor={BG};" + ("dashed=1;" if dashed else ""))
        c(f'<mxCell id="{nid()}" value="{_attr(label)}" style="{style}" edge="1" parent="1">'
          f'<mxGeometry relative="1" as="geometry">'
          f'<mxPoint x="{sx}" y="{sy}" as="sourcePoint"/><mxPoint x="{tx}" y="{ty}" as="targetPoint"/>'
          + (f'<Array as="points">{mids}</Array>' if mids else "")
          + '</mxGeometry></mxCell>')

    legend = ("<b>LEGENDA</b><br><br>"
              f"<font color='{ACTIVE}'>■ borda sólida verde</font> = ATIVO (conectado em runtime via hook, MCP ou daemon)<br><br>"
              f"<font color='{LIBRARY}'>▢ borda tracejada âmbar</font> = BIBLIOTECA (implementado e testado, sem adaptador que o chame ainda)<br><br>"
              "seta sólida = fluxo real · seta tracejada = fluxo previsto<br><br>"
              f"<font color='{MUTED}'>Python stdlib 3.10+ · arquitetura hexagonal</font>")
    c(f'<mxCell id="legend" value="{_attr(legend)}" style="rounded=1;arcSize=4;whiteSpace=wrap;html=1;'
      f'fillColor={LAYER_FILL};strokeColor={MUTED};fontColor={TEXT};fontSize=12;align=left;verticalAlign=top;'
      f'spacingLeft=12;spacingTop=8;" vertex="1" parent="1"><mxGeometry x="1270" y="100" width="290" height="300" '
      f'as="geometry"/></mxCell>')

    body = "\n        ".join(cells)
    return f"""<mxfile host="app.diagrams.net" agent="Antigravity" version="21.0.0" type="device">
  <diagram id="agentic-layers" name="Camadas de Ação Agêntica">
    <mxGraphModel dx="1600" dy="1260" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{W}" pageHeight="{H}" background="{BG}" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {body}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""


def main() -> None:
    os.makedirs(os.path.dirname(SVG_OUT), exist_ok=True)
    with open(SVG_OUT, "w", encoding="utf-8") as f:
        f.write(_svg())
    with open(DRAWIO_OUT, "w", encoding="utf-8") as f:
        f.write(_drawio())
    print(f"wrote {os.path.relpath(SVG_OUT, ROOT)}")
    print(f"wrote {os.path.relpath(DRAWIO_OUT, ROOT)}")


if __name__ == "__main__":
    main()
