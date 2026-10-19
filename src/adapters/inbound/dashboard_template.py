"""
Dashboard HTML/JS Template for Telemetry 360.
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Antigravity Telemetry & Efficiency Matrix</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    :root {
      --bg: #090d13;
      --card-bg: #121820;
      --card-inner: #1a222d;
      --border: #263242;
      --text: #cbd5e1;
      --heading: #f8fafc;
      --accent: #38bdf8;
      --green: #22c55e;
      --purple: #c084fc;
      --amber: #f59e0b;
      --rose: #fb7185;
    }
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 24px;
      line-height: 1.5;
    }
    .container { max-width: 1240px; margin: 0 auto; }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 24px;
      flex-wrap: wrap;
      gap: 12px;
    }
    h1 { margin: 0; color: var(--heading); font-size: 22px; display: flex; align-items: center; gap: 10px; font-weight: 700; }
    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(34, 197, 94, 0.12);
      color: var(--green);
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 600;
      border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .dot { width: 8px; height: 8px; background: var(--green); border-radius: 50%; box-shadow: 0 0 8px var(--green); }
    
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px;
      position: relative;
      overflow: hidden;
    }
    .card-title { font-size: 12px; text-transform: uppercase; letter-spacing: 0.6px; color: #94a3b8; margin-bottom: 8px; font-weight: 600; }
    .card-value { font-size: 26px; font-weight: 800; color: var(--heading); }
    .card-sub { font-size: 12px; margin-top: 6px; color: #64748b; }
    
    .breakdown-bar-container {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px;
      margin-bottom: 24px;
    }
    .bar-title { display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; margin-bottom: 12px; color: var(--heading); }
    .bar {
      display: flex;
      height: 14px;
      border-radius: 8px;
      overflow: hidden;
      background: #1e293b;
      margin-bottom: 12px;
    }
    .bar-seg { height: 100%; transition: width 0.4s ease; }
    .legend { display: flex; flex-wrap: wrap; gap: 16px; font-size: 12px; }
    .legend-item { display: flex; align-items: center; gap: 6px; }
    .legend-color { width: 10px; height: 10px; border-radius: 3px; }

    .two-cols {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 24px;
    }
    @media (max-width: 900px) { .two-cols { grid-template-columns: 1fr; } }
    
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); font-size: 13px; }
    th { color: #94a3b8; font-weight: 600; font-size: 12px; text-transform: uppercase; }
    tr:hover { background: rgba(255,255,255,0.02); }
    
    .tag {
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-weight: 600;
    }
    .tag-blue { background: rgba(56, 189, 248, 0.12); color: var(--accent); }
    .tag-green { background: rgba(34, 197, 94, 0.12); color: var(--green); }
    .tag-purple { background: rgba(192, 132, 252, 0.12); color: var(--purple); }
    .tag-amber { background: rgba(245, 158, 11, 0.12); color: var(--amber); }
    
    .toggle-group {
      display: inline-flex;
      background: #1a222d;
      border: 1px solid var(--border);
      border-radius: 9999px;
      padding: 3px;
      gap: 4px;
    }
    .toggle-btn {
      background: transparent;
      border: none;
      color: #94a3b8;
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .toggle-btn.active {
      background: var(--accent);
      color: #090d13;
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
    }
    .toggle-btn:hover:not(.active) {
      color: #f8fafc;
    }

    .footer { text-align: center; margin-top: 32px; font-size: 12px; color: #64748b; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>⚡ Antigravity Dev Efficiency Matrix</h1>
      <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
        <div class="toggle-group">
          <button id="btn-mode-eng" class="toggle-btn active" onclick="switchMode('engineering')">⚡ Engenharia</button>
          <button id="btn-mode-story" class="toggle-btn" onclick="switchMode('storytelling')">📖 Storytelling (Leigo)</button>
        </div>
        <div class="toggle-group">
          <button id="btn-view-global" class="toggle-btn active" onclick="switchView('global')">🌐 Global</button>
          <button id="btn-view-session" class="toggle-btn" onclick="switchView('session')">⚡ Sessão</button>
        </div>
        <span class="status-pill"><span class="dot"></span> Cluster Local & Guardrails Ativos</span>
      </div>
    </header>

    <!-- Storytelling Section (Human Metaphors for Non-Engineers) -->
    <div id="storytelling-section" style="display: none; margin-bottom: 24px;">
      <div class="card" style="background: linear-gradient(135deg, #131b26 0%, #0d141e 100%); border-color: rgba(56, 189, 248, 0.4); margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
          <h2 style="margin: 0; font-size: 18px; color: var(--heading); display: flex; align-items: center; gap: 8px;">
            🌪️ <strong>O Efeito da Singularidade Gravitacional (Storytelling Executivo)</strong>
          </h2>
          <span class="status-pill" style="background: rgba(34, 197, 94, 0.15); color: var(--green); border-color: rgba(34, 197, 94, 0.3);">
            ✨ 88% Menos Ruído de Nuvem
          </span>
        </div>
        <p style="color: #94a3b8; font-size: 14px; margin: 0 0 16px 0; line-height: 1.6;" id="story-headline">
          Em vez de enviar documentos gigantescos para a nuvem a cada segundo gastando dinheiro, a máquina usa modelos locais no seu Mac para engolir o ruído e enviar apenas a essência cirúrgica.
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px;">
          <div style="background: rgba(56, 189, 248, 0.06); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 8px; padding: 14px;">
            <div style="font-size: 24px; margin-bottom: 4px;">📚</div>
            <div style="font-size: 20px; font-weight: 800; color: #38bdf8;" id="story-books">-- Livros</div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">Equivalente em livros inteiros de 300 páginas processados sem pagar nada de nuvem.</div>
          </div>
          <div style="background: rgba(34, 197, 94, 0.06); border: 1px solid rgba(34, 197, 94, 0.2); border-radius: 8px; padding: 14px;">
            <div style="font-size: 24px; margin-bottom: 4px;">☕</div>
            <div style="font-size: 20px; font-weight: 800; color: #22c55e;" id="story-coffees">-- Cafés</div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">R$ <span id="story-reals">0.00</span> poupados em faturas de API comercial (ou meses de servidores).</div>
          </div>
          <div style="background: rgba(245, 158, 11, 0.06); border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 8px; padding: 14px;">
            <div style="font-size: 24px; margin-bottom: 4px;">🛡️</div>
            <div style="font-size: 20px; font-weight: 800; color: #fbbf24;" id="story-rework">0 Quebras</div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">Erros e bugs barrados antes de encostar no seu código, eliminando retrabalho.</div>
          </div>
          <div style="background: rgba(192, 132, 252, 0.06); border: 1px solid rgba(192, 132, 252, 0.2); border-radius: 8px; padding: 14px;">
            <div style="font-size: 24px; margin-bottom: 4px;">⚡</div>
            <div style="font-size: 20px; font-weight: 800; color: #c084fc;" id="story-factor">8.4x Menos Carga</div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">Para cada 1 real gasto, você produz o equivalente a mais de 8 reais de valor bruto.</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Interactive Journey Pipeline Card -->
    <div class="card" style="margin-bottom: 24px; border-color: rgba(56, 189, 248, 0.3); background: linear-gradient(180deg, #131a24 0%, #0d121a 100%);">
      <div class="bar-title" style="margin-bottom: 14px;">
        <span style="display: flex; align-items: center; gap: 8px;">
          🚀 <strong>A Jornada de Uma Chamada: Do Prompt aos Modelos e Entrega</strong>
        </span>
        <span style="font-size: 11px; color: #94a3b8;">Clique nos nós para inspecionar</span>
      </div>

      <!-- 5-Stage Interactive Pipeline -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-bottom: 14px;" id="journey-pipeline-nodes">
        <!-- Rendered by JS -->
      </div>

      <!-- Dynamic Node Inspection Card -->
      <div id="journey-inspect-card" style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border); border-radius: 8px; padding: 14px; font-size: 13px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <strong id="inspect-title" style="color: var(--accent); font-size: 14px;">1. Entrada Bruta</strong>
          <span class="tag tag-blue" id="inspect-actor">Engenheiro</span>
        </div>
        <p id="inspect-story" style="margin: 0 0 8px 0; color: #cbd5e1; line-height: 1.5;">
          A instrução chega com perguntas e código. Sem filtros, isso consumiria de 50.000 a 100.000 tokens desnecessários.
        </p>
        <div style="font-size: 12px; color: var(--green); font-weight: 600;" id="inspect-impact">
          Impacto: Ponto de partida do pipeline
        </div>
      </div>
    </div>

    <div class="grid">
      <div class="card">
        <div class="card-title">Tokens Poupados (Gross)</div>
        <div class="card-value" id="tokens-saved" style="color: var(--green);">--</div>
        <div class="card-sub" id="cost-saved">Economia: $0.00 USD</div>
      </div>
      <div class="card">
        <div class="card-title">Eficiência Global</div>
        <div class="card-value" id="efficiency-rate" style="color: var(--accent);">--%</div>
        <div class="card-sub">Carga total reduzida</div>
      </div>
      <div class="card">
        <div class="card-title">Offload Local Mac</div>
        <div class="card-value" id="local-tokens" style="color: var(--purple);">--</div>
        <div class="card-sub">Processados 100% no Mac</div>
      </div>
      <div class="card">
        <div class="card-title">Guardrail In-Memory AST</div>
        <div class="card-value" style="color: var(--amber);">Ativo (0 Quebras)</div>
        <div class="card-sub">Pre-Tool Hook validando patches</div>
      </div>
      <div class="card">
        <div class="card-title">Ruído Terminal Cortado</div>
        <div class="card-value" id="lines-saved" style="color: var(--rose);">-- linhas</div>
        <div class="card-sub">Test Slicer & RTK hooks</div>
      </div>
      <div class="card">
        <div class="card-title">Projeção Mensal Poupada</div>
        <div class="card-value" id="monthly-proj" style="color: var(--green);">$0.00</div>
        <div class="card-sub">Estimativa 30 dias</div>
      </div>
      <div class="card" style="border-color: rgba(56, 189, 248, 0.4); background: rgba(56, 189, 248, 0.04);">
        <div class="card-title">Custo Efetivo Real (Gasto)</div>
        <div class="card-value" id="cost-consumed" style="color: var(--accent);">$0.00 USD</div>
        <div class="card-sub" id="tokens-consumed-sub">-- tokens pagos em nuvem</div>
      </div>
    </div>

    <!-- Comparative Real-Time Chart: Economizado vs Gasto sem a Suite -->
    <div class="breakdown-bar-container" style="background: linear-gradient(180deg, #161e2a 0%, #10161f 100%); border-color: rgba(56, 189, 248, 0.35); margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
      <div class="bar-title">
        <span style="display: flex; align-items: center; gap: 8px;">
          📊 <strong>Economizado vs Gasto sem a Suite (Tempo Real)</strong>
        </span>
        <span class="status-pill" style="background: rgba(56, 189, 248, 0.15); color: var(--accent); border-color: rgba(56, 189, 248, 0.3);" id="factor-badge">
          ⚡ 8.8x Menos Tokens Gastos
        </span>
      </div>

      <div style="margin: 18px 0;">
        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px;">
          <span style="color: #f87171; font-weight: 600;">🔴 Gasto Projetado SEM a Suite (Leitura Total, Sem RAG/AST, Sem Patch)</span>
          <span id="cmp-unoptimized" style="color: #f87171; font-weight: 700;">-- tokens</span>
        </div>
        <div class="bar" style="height: 18px; background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3);">
          <div style="background: linear-gradient(90deg, #ef4444 0%, #f87171 100%); width: 100%; height: 100%; border-radius: 6px;"></div>
        </div>

        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; margin-top: 14px;">
          <span style="color: #38bdf8; font-weight: 600;">🟢 Tokens Reais Pagos na Nuvem COM a Suite Event Horizon</span>
          <span id="cmp-optimized" style="color: #38bdf8; font-weight: 700;">-- tokens</span>
        </div>
        <div class="bar" style="height: 18px; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.3);">
          <div id="cmp-bar-optimized" style="background: linear-gradient(90deg, #0284c7 0%, #38bdf8 100%); width: 11.4%; height: 100%; border-radius: 6px; transition: width 0.6s ease;"></div>
        </div>
      </div>

      <div style="display: flex; justify-content: space-between; font-size: 12px; color: #94a3b8; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px; flex-wrap: wrap; gap: 8px;">
        <span>Margem de Economia Direta: <strong id="cmp-tokens-saved" style="color: var(--green);">-- tokens</strong></span>
        <span>Economia Financeira Acumulada: <strong id="cmp-cost-saved" style="color: var(--green);">$0.00 USD</strong></span>
      </div>
    </div>

    <div class="breakdown-bar-container">
      <div class="bar-title">
        <span>Distribuição de Redução de Tokens por Mecanismo</span>
        <span id="total-gross-saved">Total: -- tokens</span>
      </div>
      <div class="bar">
        <div class="bar-seg" id="seg-cache" style="background: var(--accent); width: 85%;"></div>
        <div class="bar-seg" id="seg-ponytail" style="background: var(--green); width: 10%;"></div>
        <div class="bar-seg" id="seg-ast" style="background: var(--purple); width: 3%;"></div>
        <div class="bar-seg" id="seg-mcp" style="background: var(--amber); width: 2%;"></div>
      </div>
      <div class="legend">
        <div class="legend-item"><div class="legend-color" style="background: var(--accent);"></div> Gemini Context Cache (<span id="pct-cache">--%</span>)</div>
        <div class="legend-item"><div class="legend-color" style="background: var(--green);"></div> Ponytail Surgical Patching (<span id="pct-ponytail">--%</span>)</div>
        <div class="legend-item"><div class="legend-color" style="background: var(--purple);"></div> AST Code Search & RAG (<span id="pct-ast">--%</span>)</div>
        <div class="legend-item"><div class="legend-color" style="background: var(--amber);"></div> Local Model Offload & Test Slicer (<span id="pct-mcp">--%</span>)</div>
      </div>
    </div>

    <!-- Multi-Provider Cost Simulator Card -->
    <div class="card" style="margin-bottom: 24px; border-color: rgba(56, 189, 248, 0.35); background: linear-gradient(180deg, #131b26 0%, #0d131c 100%);">
      <div class="bar-title" style="margin-bottom: 16px;">
        <span style="display: flex; align-items: center; gap: 8px;">
          💰 <strong>Simulador Multi-Provedor: Custo Sem Otimização vs Net Pago Real</strong>
        </span>
        <span class="status-pill" style="background: rgba(34, 197, 94, 0.15); color: var(--green); border-color: rgba(34, 197, 94, 0.3);" id="provider-net-savings-badge">
          Economia Líquida: +$0.00 USD
        </span>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px;">
        <!-- OpenAI GPT-4o -->
        <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 14px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <strong style="color: #34d399; font-size: 13px;">OpenAI GPT-4o</strong>
            <span class="tag tag-green" id="gpt4o-pct-saved">-88.1%</span>
          </div>
          <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;">Sem Otimização: <span id="gpt4o-unopt" style="color: #f87171; text-decoration: line-through;">$0.00</span></div>
          <div style="font-size: 16px; font-weight: 800; color: #f8fafc;" id="gpt4o-net">$0.00 <span style="font-size: 11px; font-weight: normal; color: #94a3b8;">com suite</span></div>
          <div style="font-size: 11px; color: var(--green); margin-top: 4px;">Poupado: <strong id="gpt4o-saved">+$0.00</strong></div>
        </div>

        <!-- Claude 3.5 Sonnet -->
        <div style="background: rgba(192, 132, 252, 0.05); border: 1px solid rgba(192, 132, 252, 0.2); border-radius: 8px; padding: 14px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <strong style="color: #c084fc; font-size: 13px;">Anthropic Claude 3.5 Sonnet</strong>
            <span class="tag tag-purple" id="claude-pct-saved">-88.1%</span>
          </div>
          <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;">Sem Otimização: <span id="claude-unopt" style="color: #f87171; text-decoration: line-through;">$0.00</span></div>
          <div style="font-size: 16px; font-weight: 800; color: #f8fafc;" id="claude-net">$0.00 <span style="font-size: 11px; font-weight: normal; color: #94a3b8;">com suite</span></div>
          <div style="font-size: 11px; color: var(--green); margin-top: 4px;">Poupado: <strong id="claude-saved">+$0.00</strong></div>
        </div>

        <!-- Google Gemini 2.0 (Base) -->
        <div style="background: rgba(56, 189, 248, 0.05); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 8px; padding: 14px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <strong style="color: #38bdf8; font-size: 13px;">Google Gemini 2.0 (Base)</strong>
            <span class="tag tag-blue" id="gemini-pct-saved">-88.1%</span>
          </div>
          <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;">Sem Otimização: <span id="gemini-unopt" style="color: #f87171; text-decoration: line-through;">$0.00</span></div>
          <div style="font-size: 16px; font-weight: 800; color: #f8fafc;" id="gemini-net">$0.00 <span style="font-size: 11px; font-weight: normal; color: #94a3b8;">com suite</span></div>
          <div style="font-size: 11px; color: var(--green); margin-top: 4px;">Poupado: <strong id="gemini-saved">+$0.00</strong></div>
        </div>

        <!-- Event Horizon Singularity -->
        <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 8px; padding: 14px; box-shadow: 0 0 15px rgba(245, 158, 11, 0.1);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <strong style="color: #fbbf24; font-size: 13px;">⚡ Event Horizon Singularity</strong>
            <span class="tag tag-amber" style="background: rgba(245, 158, 11, 0.25);">TIER 0 LOCAL</span>
          </div>
          <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;">Redução Fatorial: <span style="color: #fbbf24; font-weight: 700;" id="eh-reduction">8.4x</span></div>
          <div style="font-size: 16px; font-weight: 800; color: #38bdf8;" id="eh-net-paid">$0.00 <span style="font-size: 11px; font-weight: normal; color: #94a3b8;">net pago</span></div>
          <div style="font-size: 11px; color: var(--green); margin-top: 4px;">Economia Direta: <strong id="eh-saved">+$0.00 USD</strong></div>
        </div>
      </div>
    </div>

    <!-- Gemini Cloud Dynamic Routing Matrix Card -->
    <div class="card" style="margin-bottom: 24px; border-color: rgba(56, 189, 248, 0.35); background: linear-gradient(180deg, #121924 0%, #0c1118 100%);">
      <div class="bar-title" style="margin-bottom: 14px;">
        <span style="display: flex; align-items: center; gap: 8px;">
          🌐 <strong>Otimização em Nuvem: Matriz de Roteamento Dinâmico Gemini</strong>
        </span>
        <span class="status-pill" style="background: rgba(56, 189, 248, 0.15); color: var(--accent); border-color: rgba(56, 189, 248, 0.3);" id="cloud-tiering-badge">
          Economia Interna Cloud: até 95%
        </span>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px;">
        <!-- Flash Lite -->
        <div style="background: rgba(56, 189, 248, 0.05); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 8px; padding: 14px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <strong style="color: #38bdf8; font-size: 13px;">Gemini 2.0 Flash-Lite</strong>
            <span class="tag tag-green">-95.0% vs Pro</span>
          </div>
          <div style="font-size: 16px; font-weight: 800; color: #f8fafc; margin-bottom: 4px;">$0.075 <span style="font-size: 11px; font-weight: normal; color: #94a3b8;">/ 1M tokens</span></div>
          <div style="font-size: 12px; color: #94a3b8; margin-bottom: 6px;">Papel: <strong>Micro-validações, lint e checks rápidos</strong></div>
          <div style="font-size: 11px; color: var(--accent);">Gatilho: Subagentes exploratórios de checagem pontual.</div>
        </div>

        <!-- Flash -->
        <div style="background: rgba(34, 197, 94, 0.05); border: 1px solid rgba(34, 197, 94, 0.2); border-radius: 8px; padding: 14px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <strong style="color: #22c55e; font-size: 13px;">Gemini 2.0 Flash</strong>
            <span class="tag tag-green">-93.3% vs Pro</span>
          </div>
          <div style="font-size: 16px; font-weight: 800; color: #f8fafc; margin-bottom: 4px;">$0.100 <span style="font-size: 11px; font-weight: normal; color: #94a3b8;">/ 1M tokens</span></div>
          <div style="font-size: 12px; color: #94a3b8; margin-bottom: 6px;">Papel: <strong>Pesquisa ampla, web search e subagentes paralelos</strong></div>
          <div style="font-size: 11px; color: var(--green);">Gatilho: Múltiplos agentes pesquisando código concorrentemente.</div>
        </div>

        <!-- Pro -->
        <div style="background: rgba(192, 132, 252, 0.05); border: 1px solid rgba(192, 132, 252, 0.2); border-radius: 8px; padding: 14px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <strong style="color: #c084fc; font-size: 13px;">Gemini 2.0 Pro</strong>
            <span class="tag tag-purple">Orquestrador Base</span>
          </div>
          <div style="font-size: 16px; font-weight: 800; color: #f8fafc; margin-bottom: 4px;">$1.500 <span style="font-size: 11px; font-weight: normal; color: #94a3b8;">/ 1M tokens</span></div>
          <div style="font-size: 12px; color: #94a3b8; margin-bottom: 6px;">Papel: <strong>Arquitetura central e planejamento complexo</strong></div>
          <div style="font-size: 11px; color: var(--purple);">Gatilho: Decisões de alto impacto, migrações e raciocínio profundo.</div>
        </div>
      </div>
    </div>

    <!-- Charts Two-Cols: Temporal Evolution & Donut Breakdown -->
    <div class="two-cols" style="margin-bottom: 24px;">
      <!-- Temporal Evolution: Burn Rate vs Savings -->
      <div class="card" style="border-color: rgba(56, 189, 248, 0.25);">
        <div class="bar-title" style="margin-bottom: 12px;">
          <span>📈 <strong>Evolução Temporal: Burn Rate vs Tokens Poupados</strong></span>
          <span style="font-size: 11px; color: #94a3b8;" id="timeline-subtitle">Passos da Sessão</span>
        </div>
        <div style="width: 100%; height: 210px; position: relative;" id="timeline-container">
          <svg id="timeline-svg" width="100%" height="100%" viewBox="0 0 540 200" preserveAspectRatio="none" style="overflow: visible;">
            <!-- Rendered by JS -->
          </svg>
        </div>
        <div style="display: flex; justify-content: center; gap: 20px; font-size: 12px; margin-top: 10px;">
          <div style="display: flex; align-items: center; gap: 6px;">
            <span style="width: 12px; height: 3px; background: #38bdf8; display: inline-block; border-radius: 2px;"></span> Tokens Poupados / Passo
          </div>
          <div style="display: flex; align-items: center; gap: 6px;">
            <span style="width: 12px; height: 3px; background: #f87171; display: inline-block; border-radius: 2px;"></span> Burn Rate (Tokens Pagos)
          </div>
        </div>
      </div>

      <!-- Interactive SVG Donut: Savings Breakdown by Layer -->
      <div class="card" style="border-color: rgba(192, 132, 252, 0.25);">
        <div class="bar-title" style="margin-bottom: 12px;">
          <span>🍩 <strong>Decomposição Anatômica de Economia (Donut 360)</strong></span>
          <span style="font-size: 11px; color: #94a3b8;">Distribuição por Camada</span>
        </div>
        <div style="display: flex; align-items: center; justify-content: center; height: 210px; gap: 20px;">
          <div style="width: 170px; height: 170px; position: relative;">
            <svg id="donut-svg" width="170" height="170" viewBox="0 0 170 170" style="transform: rotate(-90deg);">
              <!-- Rendered by JS -->
            </svg>
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; pointer-events: none;">
              <span id="donut-center-pct" style="font-size: 22px; font-weight: 800; color: var(--heading);">88%</span>
              <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Eficiência</span>
            </div>
          </div>
          <div id="donut-legend" style="display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
            <!-- Dynamic Legend items -->
          </div>
        </div>
      </div>
    </div>

    <div class="two-cols">
      <div class="card">
        <div class="card-title">Cluster de Modelos de IA Locais (Ollama no Mac)</div>
        <table>
          <thead>
            <tr>
              <th>Modelo</th>
              <th>Tamanho</th>
              <th>Papel Agêntico</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody id="models-table"></tbody>
        </table>
      </div>

      <div class="card">
        <div class="card-title">Eficiência por Skill & Abstração</div>
        <table>
          <thead>
            <tr>
              <th>Mecanismo / Skill</th>
              <th>Usos</th>
              <th>Tokens Evitados</th>
              <th>Estratégia</th>
            </tr>
          </thead>
          <tbody id="skills-table"></tbody>
        </table>
      </div>
    </div>

    <!-- Local Models Utilization Chart Card -->
    <div class="card" style="margin-bottom: 24px; border-color: rgba(192, 132, 252, 0.35); background: linear-gradient(180deg, #151b26 0%, #10151d 100%);">
      <div class="bar-title" style="margin-bottom: 18px;">
        <span style="display: flex; align-items: center; gap: 8px;">
          🧠 <strong>Utilização por Modelo Local no Mac (Tokens Offloaded & Invocações)</strong>
        </span>
        <span class="status-pill" style="background: rgba(192, 132, 252, 0.15); color: var(--purple); border-color: rgba(192, 132, 252, 0.3);" id="local-models-total-badge">
          -- tokens offloaded no Mac
        </span>
      </div>
      <div id="local-models-bars" style="display: flex; flex-direction: column; gap: 14px;">
        <!-- Dynamic horizontal bars rendered by JavaScript -->
      </div>
    </div>

    <div class="card">
      <div class="card-title">Histórico Recente de Interceptações e Operações Zero-Token</div>
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Mecanismo</th>
            <th>Detalhe da Operação</th>
            <th>Tokens Poupados</th>
          </tr>
        </thead>
        <tbody id="events-table"></tbody>
      </table>
    </div>

    <div class="footer">
      Antigravity Telemetry Matrix • Porta 7890 • Atualização automática a cada 3 segundos • Apple Silicon M-Series
    </div>
  </div>

  <script>
    let cachedData = null;
    let currentView = 'global'; // 'global' or 'session'
    let currentMode = 'engineering'; // 'engineering' or 'storytelling'

    function switchMode(mode) {
      currentMode = mode;
      document.getElementById('btn-mode-eng').classList.toggle('active', mode === 'engineering');
      document.getElementById('btn-mode-story').classList.toggle('active', mode === 'storytelling');
      const storySec = document.getElementById('storytelling-section');
      if (storySec) {
        storySec.style.display = (mode === 'storytelling') ? 'block' : 'none';
      }
    }

    function switchView(view) {
      currentView = view;
      document.getElementById('btn-view-global').classList.toggle('active', view === 'global');
      document.getElementById('btn-view-session').classList.toggle('active', view === 'session');
      if (cachedData) renderView();
    }

    let activeJourneyIndex = 0;
    function renderJourney(nodes) {
      const container = document.getElementById('journey-pipeline-nodes');
      if (!container || !nodes || !nodes.length) return;
      container.innerHTML = '';

      nodes.forEach((node, idx) => {
        const item = document.createElement('div');
        const isActive = (idx === activeJourneyIndex);
        item.style.cssText = `
          background: ${isActive ? 'rgba(56, 189, 248, 0.12)' : 'rgba(255, 255, 255, 0.03)'};
          border: 1px solid ${isActive ? 'var(--accent)' : 'var(--border)'};
          border-radius: 8px;
          padding: 10px 12px;
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          flex-direction: column;
          gap: 4px;
        `;
        item.onclick = () => {
          activeJourneyIndex = idx;
          renderJourney(nodes);
          inspectJourneyNode(nodes[idx]);
        };
        item.innerHTML = `
          <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 18px;">${node.icon || '🔹'}</span>
            <span class="tag ${isActive ? 'tag-blue' : 'tag-purple'}" style="font-size: 10px;">${node.id.toUpperCase()}</span>
          </div>
          <div style="font-weight: 700; font-size: 13px; color: ${isActive ? 'var(--accent)' : 'var(--heading)'};">${node.title}</div>
          <div style="font-size: 11px; color: #94a3b8;">${node.actor}</div>
        `;
        container.appendChild(item);
      });
      inspectJourneyNode(nodes[activeJourneyIndex]);
    }

    function inspectJourneyNode(node) {
      if (!node) return;
      document.getElementById('inspect-title').innerText = `${node.icon || ''} ${node.title}`;
      document.getElementById('inspect-actor').innerText = node.actor;
      document.getElementById('inspect-story').innerText = node.story;
      document.getElementById('inspect-impact').innerText = `⚡ ${node.status}`;
    }

    function renderDonut(skillsBreakdown, cacheTokens, totalSaved) {
      const svg = document.getElementById('donut-svg');
      const legend = document.getElementById('donut-legend');
      if (!svg || !legend) return;

      const items = [
        { name: 'Gemini Context Cache', tokens: cacheTokens || 0, color: '#38bdf8' },
        { name: 'Ponytail Patching', tokens: skillsBreakdown['ponytail-patching']?.tokens_saved || 0, color: '#22c55e' },
        { name: 'Zero-Cloud Drafts', tokens: skillsBreakdown['zero-cloud-drafts']?.tokens_saved || 0, color: '#06b6d4' },
        { name: 'AST Code Search & RAG', tokens: skillsBreakdown['ast-search']?.tokens_saved || 0, color: '#c084fc' },
        { name: 'Local Ollama Offload', tokens: skillsBreakdown['local-llm-mcp']?.tokens_saved || 0, color: '#f59e0b' },
        { name: 'Terminal Truncation', tokens: skillsBreakdown['smart-test-slicer']?.tokens_saved || 0, color: '#fb7185' }
      ];

      const safeTotal = Math.max(1, totalSaved);
      const r = 62;
      const c = 2 * Math.PI * r;
      let accOffset = 0;
      
      svg.innerHTML = '';
      legend.innerHTML = '';

      const bgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      bgCircle.setAttribute('cx', '85');
      bgCircle.setAttribute('cy', '85');
      bgCircle.setAttribute('r', r);
      bgCircle.setAttribute('fill', 'none');
      bgCircle.setAttribute('stroke', '#1e293b');
      bgCircle.setAttribute('stroke-width', '18');
      svg.appendChild(bgCircle);

      for (const item of items) {
        const pct = item.tokens / safeTotal;
        if (pct > 0.005) {
          const dash = pct * c;
          const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
          circle.setAttribute('cx', '85');
          circle.setAttribute('cy', '85');
          circle.setAttribute('r', r);
          circle.setAttribute('fill', 'none');
          circle.setAttribute('stroke', item.color);
          circle.setAttribute('stroke-width', '18');
          circle.setAttribute('stroke-dasharray', `${dash} ${c - dash}`);
          circle.setAttribute('stroke-dashoffset', -accOffset);
          circle.setAttribute('stroke-linecap', 'round');
          circle.style.transition = 'stroke-dasharray 0.5s ease, stroke-dashoffset 0.5s ease';
          svg.appendChild(circle);
          accOffset += dash;
        }

        const leg = document.createElement('div');
        leg.style.cssText = 'display: flex; align-items: center; justify-content: space-between; gap: 12px;';
        leg.innerHTML = `
          <div style="display: flex; align-items: center; gap: 6px;">
            <span style="width: 8px; height: 8px; border-radius: 2px; background: ${item.color};"></span>
            <span style="color: #cbd5e1;">${item.name}</span>
          </div>
          <span style="font-weight: 700; color: #f8fafc;">${(pct * 100).toFixed(1)}%</span>
        `;
        legend.appendChild(leg);
      }
    }

    function renderTimeline(timeline) {
      const svg = document.getElementById('timeline-svg');
      if (!svg) return;

      const points = timeline && timeline.length ? timeline : [
        { burned: 12000, saved: 85000, step: 1 },
        { burned: 14000, saved: 92000, step: 2 }
      ];

      const w = 540;
      const h = 200;
      const padL = 40;
      const padR = 20;
      const padT = 20;
      const padB = 30;
      const plotW = w - padL - padR;
      const plotH = h - padT - padB;

      const maxVal = Math.max(1, ...points.map(p => Math.max(p.burned || 0, p.saved || 0)));

      let savedCoords = [];
      let burnedCoords = [];

      for (let i = 0; i < points.length; i++) {
        const x = padL + (i / Math.max(1, points.length - 1)) * plotW;
        const yS = (padT + plotH) - ((points[i].saved || 0) / maxVal) * plotH;
        const yB = (padT + plotH) - ((points[i].burned || 0) / maxVal) * plotH;
        savedCoords.push({ x, y: yS, val: points[i].saved, step: points[i].step });
        burnedCoords.push({ x, y: yB, val: points[i].burned, step: points[i].step });
      }

      function buildPath(coords) {
        return coords.reduce((acc, pt, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${pt.x.toFixed(1)},${pt.y.toFixed(1)}`, '');
      }

      function buildArea(coords) {
        if (!coords.length) return '';
        const baseline = (padT + plotH).toFixed(1);
        const line = buildPath(coords);
        return `${line} L ${coords[coords.length - 1].x.toFixed(1)},${baseline} L ${coords[0].x.toFixed(1)},${baseline} Z`;
      }

      let gridSvg = '';
      for (let g = 0; g <= 4; g++) {
        const yG = padT + (g / 4) * plotH;
        const vG = Math.round(maxVal * (1 - g / 4));
        gridSvg += `
          <line x1="${padL}" y1="${yG}" x2="${w - padR}" y2="${yG}" stroke="rgba(255,255,255,0.06)" stroke-dasharray="3 3" />
          <text x="${padL - 6}" y="${yG + 4}" fill="#64748b" font-size="9" text-anchor="end">${(vG >= 1000 ? (vG/1000).toFixed(0) + 'k' : vG)}</text>
        `;
      }

      let dotsSvg = '';
      savedCoords.forEach(pt => {
        dotsSvg += `<circle cx="${pt.x.toFixed(1)}" cy="${pt.y.toFixed(1)}" r="3" fill="#38bdf8"><title>Passo ${pt.step}: +${(pt.val||0).toLocaleString()} tokens poupados</title></circle>`;
      });
      burnedCoords.forEach(pt => {
        dotsSvg += `<circle cx="${pt.x.toFixed(1)}" cy="${pt.y.toFixed(1)}" r="2.5" fill="#f87171"><title>Passo ${pt.step}: ${(pt.val||0).toLocaleString()} tokens pagos</title></circle>`;
      });

      svg.innerHTML = `
        ${gridSvg}
        <path d="${buildArea(savedCoords)}" fill="rgba(56, 189, 248, 0.12)" />
        <path d="${buildPath(savedCoords)}" fill="none" stroke="#38bdf8" stroke-width="2.5" />
        <path d="${buildPath(burnedCoords)}" fill="none" stroke="#f87171" stroke-width="2" stroke-dasharray="4 2" />
        ${dotsSvg}
      `;
    }

    function renderView() {
      if (!cachedData) return;
      const isSess = (currentView === 'session' && cachedData.session);
      const d = isSess ? cachedData.session : cachedData;

      document.getElementById('tokens-saved').innerText = (d.total_tokens_saved || 0).toLocaleString();
      document.getElementById('cost-saved').innerText = `Economia: $${(d.cost_saved_usd || 0).toFixed(4)} USD`;
      document.getElementById('efficiency-rate').innerText = `${d.efficiency_rate_pct || 0}%`;
      document.getElementById('local-tokens').innerText = (d.local_tokens_saved || 0).toLocaleString();
      document.getElementById('lines-saved').innerText = `${(d.terminal_lines_saved || 0).toLocaleString()} lns`;
      document.getElementById('monthly-proj').innerText = `$${((d.cost_saved_usd || 0) * 3.5).toFixed(2)} USD`;
      document.getElementById('cost-consumed').innerText = `$${(d.cost_consumed_usd || 0).toFixed(4)} USD`;
      document.getElementById('tokens-consumed-sub').innerText = `${(d.total_tokens_consumed || 0).toLocaleString()} tokens pagos em nuvem`;
      document.getElementById('total-gross-saved').innerText = `Total: ${(d.total_tokens_saved || 0).toLocaleString()} tokens`;

      const unopt = d.projected_unoptimized_tokens || 1;
      const opt = d.total_tokens_consumed || 0;
      document.getElementById('cmp-unoptimized').innerText = `${unopt.toLocaleString()} tokens`;
      document.getElementById('cmp-optimized').innerText = `${opt.toLocaleString()} tokens`;
      document.getElementById('factor-badge').innerText = `⚡ ${d.reduction_factor || 1}x Menos Tokens Gastos`;
      document.getElementById('cmp-tokens-saved').innerText = `+${(d.total_tokens_saved || 0).toLocaleString()} tokens`;
      document.getElementById('cmp-cost-saved').innerText = `$${(d.cost_saved_usd || 0).toFixed(4)} USD`;

      const pctUsed = Math.min(100, Math.max(1, (opt / unopt * 100)));
      document.getElementById('cmp-bar-optimized').style.width = `${pctUsed.toFixed(1)}%`;

      const prov = d.providers || cachedData.providers;
      if (prov) {
        document.getElementById('provider-net-savings-badge').innerText = `Economia Líquida: +$${(prov.net_saved_usd || 0).toFixed(2)} USD`;
        if (prov.gpt4o) {
          document.getElementById('gpt4o-pct-saved').innerText = `-${prov.gpt4o.pct}%`;
          document.getElementById('gpt4o-unopt').innerText = `$${prov.gpt4o.unopt.toFixed(2)}`;
          document.getElementById('gpt4o-net').innerHTML = `$${prov.gpt4o.net.toFixed(2)} <span style="font-size: 11px; font-weight: normal; color: #94a3b8;">com suite</span>`;
          document.getElementById('gpt4o-saved').innerText = `+$${prov.gpt4o.saved.toFixed(2)}`;
        }
        if (prov.claude) {
          document.getElementById('claude-pct-saved').innerText = `-${prov.claude.pct}%`;
          document.getElementById('claude-unopt').innerText = `$${prov.claude.unopt.toFixed(2)}`;
          document.getElementById('claude-net').innerHTML = `$${prov.claude.net.toFixed(2)} <span style="font-size: 11px; font-weight: normal; color: #94a3b8;">com suite</span>`;
          document.getElementById('claude-saved').innerText = `+$${prov.claude.saved.toFixed(2)}`;
        }
        if (prov.gemini) {
          document.getElementById('gemini-pct-saved').innerText = `-${prov.gemini.pct}%`;
          document.getElementById('gemini-unopt').innerText = `$${prov.gemini.unopt.toFixed(2)}`;
          document.getElementById('gemini-net').innerHTML = `$${prov.gemini.net.toFixed(2)} <span style="font-size: 11px; font-weight: normal; color: #94a3b8;">com suite</span>`;
          document.getElementById('gemini-saved').innerText = `+$${prov.gemini.saved.toFixed(2)}`;
        }
        document.getElementById('eh-reduction').innerText = `${d.reduction_factor || 1}x`;
        document.getElementById('eh-net-paid').innerHTML = `$${(prov.actual_net_paid_usd || 0).toFixed(2)} <span style="font-size: 11px; font-weight: normal; color: #94a3b8;">net pago</span>`;
        document.getElementById('eh-saved').innerText = `+$${(prov.net_saved_usd || 0).toFixed(2)} USD`;
      }

      const total = d.total_tokens_saved || 1;
      const cacheTok = d.cache_read_tokens || 0;
      const ponyTok = d.skills_breakdown['ponytail-patching']?.tokens_saved || 0;
      const astTok = d.skills_breakdown['ast-search']?.tokens_saved || 0;
      const mcpTok = (d.skills_breakdown['local-llm-mcp']?.tokens_saved || 0) + (d.skills_breakdown['smart-test-slicer']?.tokens_saved || 0);

      const pCache = Math.max(1, (cacheTok / total * 100));
      const pPony = Math.max(1, (ponyTok / total * 100));
      const pAst = Math.max(1, (astTok / total * 100));
      const pMcp = Math.max(1, (mcpTok / total * 100));

      document.getElementById('seg-cache').style.width = `${pCache}%`;
      document.getElementById('seg-ponytail').style.width = `${pPony}%`;
      document.getElementById('seg-ast').style.width = `${pAst}%`;
      document.getElementById('seg-mcp').style.width = `${pMcp}%`;

      document.getElementById('pct-cache').innerText = `${pCache.toFixed(1)}%`;
      document.getElementById('pct-ponytail').innerText = `${pPony.toFixed(1)}%`;
      document.getElementById('pct-ast').innerText = `${pAst.toFixed(1)}%`;
      document.getElementById('pct-mcp').innerText = `${pMcp.toFixed(1)}%`;

      document.getElementById('donut-center-pct').innerText = `${d.efficiency_rate_pct || 0}%`;
      renderDonut(d.skills_breakdown, d.cache_read_tokens, d.total_tokens_saved);

      const tl = isSess ? (d.timeline || []) : (cachedData.timeline || []);
      const sub = document.getElementById('timeline-subtitle');
      if (sub) sub.innerText = isSess ? `Sessão Ativa: ${tl.length} Passos` : `Histórico Recente: ${tl.length} Passos`;
      renderTimeline(tl);

      const sTable = document.getElementById('skills-table');
      sTable.innerHTML = '';
      for (const [k, v] of Object.entries(d.skills_breakdown)) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>${k}</strong></td>
          <td>${v.invocations}</td>
          <td style="color: var(--green); font-weight: 700;">+${v.tokens_saved.toLocaleString()}</td>
          <td><span class="tag tag-purple">${v.type}</span></td>
        `;
        sTable.appendChild(tr);
      }

      if (cachedData.storytelling) {
        const st = cachedData.storytelling;
        const sBooks = document.getElementById('story-books');
        const sCoffees = document.getElementById('story-coffees');
        const sReals = document.getElementById('story-reals');
        const sRework = document.getElementById('story-rework');
        const sFactor = document.getElementById('story-factor');
        const sHead = document.getElementById('story-headline');

        if (sBooks) sBooks.innerText = `${st.books_saved.toLocaleString()} Livros`;
        if (sCoffees) sCoffees.innerText = `${st.coffees_saved.toLocaleString()} Cafés`;
        if (sReals) sReals.innerText = st.reals_saved.toFixed(2);
        if (sRework) sRework.innerText = `${st.rework_prevented} Quebras`;
        if (sFactor) sFactor.innerText = `${d.reduction_factor || 8.4}x Menos Carga`;
        if (sHead) sHead.innerText = st.headline;
      }

      if (cachedData.journey_nodes) {
        renderJourney(cachedData.journey_nodes);
      }
    }

    async function updateData() {
      try {
        const res = await fetch('/api/stats');
        cachedData = await res.json();
        renderView();

        const mTable = document.getElementById('models-table');
        mTable.innerHTML = '';
        for (const m of (cachedData.local_models || [])) {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td><strong>${m.name}</strong></td>
            <td>${m.size_gb} GB</td>
            <td><span class="tag tag-blue">${m.role}</span></td>
            <td><span class="tag tag-green">Pronto</span></td>
          `;
          mTable.appendChild(tr);
        }

        const mBars = document.getElementById('local-models-bars');
        const mBadge = document.getElementById('local-models-total-badge');
        if (mBars && cachedData.local_models_usage) {
          const usage = cachedData.local_models_usage;
          mBadge.innerText = `⚡ ${(usage.total_tokens || 0).toLocaleString()} tokens offloaded (${usage.total_invocations || 0} execuções)`;
          mBars.innerHTML = '';
          const models = usage.models || {};
          const maxTokens = Math.max(1, ...Object.values(models).map(m => m.tokens || 0));

          const modelColors = {
            'deepseek-r1:1.5b': 'linear-gradient(90deg, #8b5cf6 0%, #c084fc 100%)',
            'qwen2.5-coder:7b': 'linear-gradient(90deg, #06b6d4 0%, #22d3ee 100%)',
            'qwen2.5-coder:3b': 'linear-gradient(90deg, #10b981 0%, #34d399 100%)',
            'hermes3:3b': 'linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)',
            'granite3-dense:2b': 'linear-gradient(90deg, #0284c7 0%, #38bdf8 100%)',
            'nomic-embed-text:latest': 'linear-gradient(90deg, #ec4899 0%, #f472b6 100%)',
            'mau-llm-1.0-c:latest': 'linear-gradient(90deg, #14b8a6 0%, #2dd4bf 100%)'
          };

          for (const [mName, mData] of Object.entries(models)) {
            const toks = mData.tokens || 0;
            const invs = mData.invocations || 0;
            const role = mData.role || 'Ollama Model';
            const pct = Math.max(3, Math.round((toks / maxTokens) * 100));
            const gradient = modelColors[mName] || 'linear-gradient(90deg, #38bdf8 0%, #818cf8 100%)';

            const item = document.createElement('div');
            item.style.cssText = 'display: flex; flex-direction: column; gap: 6px;';
            item.innerHTML = `
              <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                  <span style="font-weight: 600; color: #f8fafc;">${mName}</span>
                  <span class="status-pill" style="font-size: 11px; padding: 2px 8px; background: rgba(56, 189, 248, 0.12); color: var(--accent); border-color: rgba(56, 189, 248, 0.25);">${role}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px; font-size: 12px;">
                  <span style="color: var(--purple); font-weight: 700;">${toks.toLocaleString()} tokens</span>
                  <span class="status-pill" style="font-size: 11px; padding: 2px 8px; background: rgba(34, 197, 94, 0.12); color: var(--green); border-color: rgba(34, 197, 94, 0.25);">${invs} invocações</span>
                </div>
              </div>
              <div class="bar" style="height: 10px; background: rgba(255, 255, 255, 0.05); border-radius: 4px; overflow: hidden;">
                <div style="background: ${gradient}; width: ${pct}%; height: 100%; border-radius: 4px; transition: width 0.5s ease;"></div>
              </div>
            `;
            mBars.appendChild(item);
          }
        }

        const eTable = document.getElementById('events-table');
        eTable.innerHTML = '';
        const evs = (cachedData.recent_events || []).slice().reverse();
        for (const ev of evs) {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td style="color:#64748b; font-size:12px;">${ev.time || 'N/A'}</td>
            <td><span class="tag tag-blue">${ev.skill}</span></td>
            <td>${ev.detail}</td>
            <td style="color: var(--green); font-weight: 700;">+${ev.saved}</td>
          `;
          eTable.appendChild(tr);
        }
      } catch (e) {
        console.error('Telemetry update error:', e);
      }
    }
    updateData();
    setInterval(updateData, 3000);
  </script>
</body>
</html>
"""
