# Changelog

Todas as alterações notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [2.3.0] - 2026-10-20

### Adicionado
- **Integração do Modelo `granite3.1-moe:3b`:**
  - Download e registro via Ollama no Apple Silicon (Metal GPU).
  - Ocupa apenas **1.4 GB de VRAM ativa** com taxa de geração de **~85 tokens/s**.
  - Papel agêntico de **Tool Master & Function Calling** adicionado ao Conselho de Agentes.
  - Mapeamento dinâmico de modelos MoE em [`src/adapters/outbound/ollama_adapter.py`](src/adapters/outbound/ollama_adapter.py).
- **Análise Arquitetural de Baixo Nível (CPython vs Cython):**
  - Documentação aprofundada no `README.md` demonstrando a superioridade da Standard Library em C nativo (`ast`, `hashlib`, `sqlite3`, `re`, `json`) sobre Cython compilado no ecossistema agêntico.
- **Expansão da Suíte de Testes Automatizados:**
  - Suíte elevada de 19 para **35 testes unitários e de integração** executados em apenas `0.007s` com 100% de aprovação.
  - Preservadas as **25 asserções E2E** de redução quantitativa de tokens.

---

## [2.2.0] - 2026-10-20

### Adicionado
- **Abstração 15: Poda Dinâmica de Contexto & Janela Deslizante Epistêmica (`EpistemicContextSqueezer`):**
  - Implementação de compactação virtual in-memory sem corromper os logs físicos de auditoria (`transcript.jsonl`).
  - Política epistêmica de 3 níveis com teto adaptativo rígido de **6.000 a 8.000 tokens**.
  - Preservação garantida de 100% dos turnos recentes ($N$ e $N-1$), artefatos de decisão e prompts do usuário.
  - Colapso seletivo de saídas longas de comandos de terminal, compilações e execuções de testes em resumos de 1 linha.
  - Value objects de domínio: `ContextSqueezePolicy`, `SqueezedContext` e `SqueezeMetrics` em [`src/domain/value_objects.py`](src/domain/value_objects.py).
  - Porta inbound [`IContextSqueezer`](src/ports/inbound/context_squeezer_port.py).
  - Caso de uso [`EpistemicContextSqueezer`](src/application/epistemic_context_squeezer.py).
  - Telemetria em tempo real `context_squeeze_metrics` conectada ao daemon na porta `:7890`.
  - Suíte de testes unitários dedicada em [`tests/unit/test_context_squeezer.py`](tests/unit/test_context_squeezer.py).

---

## [2.1.0] - 2026-10-20

### Adicionado
- **Abstração 14: Cache Epistêmico Determinístico & Memoização Semântica (L1 RAM + L2 SQLite WAL):**
  - Sistema de memoização sub-milissegundo para esqueletos AST, inspeções e análises determinísticas.
  - Chave composta tripla imutável: `SHA-256(content_sha256 : prompt_hash : tool_spec)`.
  - Invalidação determinística imediata por byte com zero risco de dados obsoletos (*stale state*).
  - Camada híbrida dupla: **L1 em RAM (LRU `<0.05ms`)** + **L2 em Disco (SQLite WAL `<0.35ms`)** nativo.
  - Value objects: `CacheKey`, `CacheEntry` e `CacheMetrics`.
  - Porta outbound [`IEpistemicCache`](src/ports/outbound/epistemic_cache_port.py) e inbound [`IEpistemicMemoizer`](src/ports/inbound/epistemic_memoizer_port.py).
  - Adaptador [`SqliteEpistemicCacheAdapter`](src/adapters/outbound/sqlite_epistemic_cache_adapter.py) e orquestrador [`EpistemicMemoizer`](src/application/epistemic_memoizer.py).
  - Telemetria `epistemic_cache_metrics` integrada ao endpoint `/api/stats`.
  - Suíte de testes unitários em [`tests/unit/test_epistemic_cache.py`](tests/unit/test_epistemic_cache.py).

---

## [2.0.0] - 2026-10-20

### Adicionado
- **Abstração 13: Arquitetura Cognitiva Dual (Sistema 1 Local Fast / Sistema 2 Nuvem Deliberativo):**
  - Implementação inspirada na *Dual-Process Theory* (Kahneman).
  - Árbitro heurístico-semântico em memória [`CognitiveArbiter`](src/application/cognitive_arbiter.py) (<0.1ms, $0.00 de nuvem).
  - Trava de circuito [`EscalationCircuitBreaker`](src/application/escalation_circuit_breaker.py) acionada após 2 falhas locais (<3s) com síntese de `EscalationPayload` (<60 tokens).
  - `TokenBudgetEnvelope` com pacing em 3 fases rígidas no Sistema 2 (Blueprint, Escrita delegada, Auditoria final).
- **Refatoração Completa para Arquitetura Hexagonal (Ports & Adapters):**
  - Reestruturação em camadas limpas: `src/domain/`, `src/ports/`, `src/application/`, `src/adapters/`.
  - Aplicação estrita dos princípios SOLID e isolamento de contratos com `typing.Protocol`.
  - Fachadas finas de retrocompatibilidade em `scripts/` mantendo comandos legados 100% operacionais.
  - Garantia de **Zero Dependências Externas** (Python Standard Library nativa).

---

## [1.2.0] - 2026-10-19

### Adicionado
- **Abstração 12: Auto-Esqueleto Proativo em `view_file` & Conversão Zero-Cloud:**
  - Interceptação automática de leituras extensas de arquivo via hook convertendo em esqueletos AST.
  - Métricas de telemetria `local_conversion_metrics` rastreando a taxa de sucesso do `local_draft_patch`.
- **A Mente Sintética do Visão (*Vision Quest Protocol*):**
  - Atualização do conceito artístico do Visão no trono cibernético cercado pelos agentes especializados.
  - Matriz formal dos paradigmas cognitivos de cada agente da mesa deliberativa.
- **Camada de Storytelling e Métricas Humanizadas:**
  - Exibição de economia em dólares e xícaras de café artesanal no dashboard `:7890`.

---

## [1.1.0] - 2026-10-18

### Adicionado
- **Roteador Especulativo Local-First (`local_draft_patch`):**
  - Draft inicial gerado pelo modelo `qwen2.5-coder:7b` local via Ollama.
  - Auto-validação de sintaxe in-memory com 1-shot self-refine retry antes de qualquer fallback de nuvem.
- **Dashboard de Telemetria 360:**
  - Servidor HTTP leve embutido servindo interface interativa em `http://127.0.0.1:7890`.
  - Curva temporal de consumo de tokens, economia acumulada e simulador multi-provedor.
- **Truncador Dinâmico de Terminal (`RTK v2 Guard`):**
  - Prevenção automática de estouro de contexto por comandos verbosos no terminal.

---

## [1.0.0] - 2026-10-18

### Adicionado
- Lançamento inicial da plataforma **Gravitational Singularity**.
- **Guardrail In-Memory Pré-Execução (`hook_pre_tool.py`)**: Validação de sintaxe antes de escrita em disco.
- **Poda Sintática de Contexto (`ast-search`)**: Redução de >68% em tokens de código.
- **RAG Semântico Local (`code-rag`)**: Vetores de 768 dimensões com `nomic-embed-text`.
- **Destilador Epistêmico de Sessão (`session-distiller`)**: Compactação de histórico com `hermes3:3b`.
- **Cirurgia de Diffs (*Ponytail Patching*)**: Modificações incrementais seguras via AST.
