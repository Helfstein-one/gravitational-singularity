<div align="center">
  <img src="assets/singularity_gravity_well.jpg" alt="Antigravity Spacetime Singularity Gravity Well" width="100%" style="border-radius: 12px; margin-bottom: 20px;" />

  # Antigravity Supercharged: Gravitational Singularity
  ### Local AI & Token Optimization Engine para Apple Silicon (MacBook Air/Pro)

  [![Status](https://img.shields.io/badge/Status-Active%20Telemetry-22c55e?style=for-the-badge)](#)
  [![Efficiency](https://img.shields.io/badge/Efficiency-88.5%25-38bdf8?style=for-the-badge)](#)
  [![Token Reduction](https://img.shields.io/badge/Token%20Reduction-8.7x-8b5cf6?style=for-the-badge)](#)
  [![Hardware](https://img.shields.io/badge/Apple%20Silicon-Metal%20Unified%20RAM-f59e0b?style=for-the-badge)](#)
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
</div>

---

> **Visão Geral:** Framework agêntico de alta contenção para o Antigravity IDE, otimizado para hardware Apple Silicon (MacBook Air/Pro M-Series, 16GB RAM) operando em arquitetura híbrida assimétrica: **Tier 0 Local (Ollama Metal)** para mecânica e RAG, e **Cloud (Gemini)** restrito para orquestração e alta cognição. Redução comprovada em produção de **8.7x** no consumo de tokens e **88.5%** de taxa de eficiência global.

---

## 🗺️ Índice & Guia da Jornada de Engenharia

Para navegar com clareza pela arquitetura, dados experimentais e implementações, a documentação técnica foi modularizada por trilhas de especialidade:

| Guia | Descrição | O Que Você Encontra |
| :--- | :--- | :--- |
| 🗺️ **[Mapa das Camadas Agênticas](docs/diagrams/agentic_layers.drawio)** | Diagrama vetorial completo & SVG | 6 camadas funcionais (Entrada, Interceptação, Cognição, Tier 0, Memória, Hardware) |
| 👥 **[Protocolo Vision Quest](docs/vision_quest.md)** | Mente sintética & Conselho de Agentes | Arte conceitual Vision Quest, 5 papéis assimétricos, paradigmas teóricos e sequência em 6 fases |
| 💡 **[Conceitos & Analogias](docs/concepts.md)** | Metáforas intuitivas & custos | Consultor em Genebra, as 5 analogias da oficina local, raio-X e fita cirúrgica |
| 🔬 **[Dissecação das 20 Abstrações](docs/abstractions.md)** | Deep-dive das 20 abstrações | Guardrails, Poda AST, RAG Local, Cascata SmolLM2, Merkle Tree e KV-Cache |
| 🧠 **[Matriz de 12 Modelos Locais](docs/models.md)** | Estudo de caso Apple Silicon 16GB | Benchmarks de VRAM, velocidade (tok/s), gráficos e tabela dos 12 modelos |
| 🏛️ **[Arquitetura Hexagonal & SOLID](docs/architecture.md)** | Design de software e fluxo E2E | Ports & Adapters, SOLID, pipeline dos 5 nós e diagrama de camadas Mermaid |
| 📈 **[Resultados & Benchmarks](docs/benchmarks.md)** | Dados quantitativos e suíte de testes | 63 testes unitários (100% PASS), 25 asserções E2E, latências e redução de tokens |
| ⚙️ **[Anatomia da Centrífuga](docs/anatomy/singularity_centrifuge.html)** | Rig laboratorial físico e spec | Visualização interativa e mapeamento mecânico da redução de tokens |

---

## 🌌 O Conceito & As 5 Analogias Práticas

O Event Horizon opera sob uma premissa astrofísica simples: **atrair, esmagar e destilar a matéria bruta do desenvolvimento (código, tracebacks, histórico) localmente no Mac com custo zero de nuvem**, enviando para a API apenas a essência pura de alta cognição.

| Analogia Prática | O Que Faz no Sistema | Modelo / Componente | Ganho de Eficiência |
| :--- | :--- | :--- | :---: |
| **1. Oficina de Artesãos Locais** | Resolve tarefas mecânicas em RAM | `smollm2:1.7b`, `deepseek-r1`, `qwen 7B` | **$0.00** de custo de nuvem |
| **2. Raio-X do Esqueleto AST** | Poda corpos imperativos mantendo tipos | `ast-search` + Merkle Engine | **>96%** menos tokens de leitura |
| **3. Guarda-Costas com Detector** | Barra quebras de sintaxe antes do SSD | `hook_pre_tool.py` (0.26ms) | **5k a 15k** tokens poupados/erro |
| **4. Fita Métrica Cirúrgica** | Proíbe reescrita integral de arquivos | `replace_file_content` (Ponytail) | **Zero** retrabalho de diff |
| **5. Destilador de Memória** | Condensa histórico de 2M tokens em fatos | `session-distiller` (`hermes3:3b`) | **<500 tokens** de memória pura |

> 💡 **Guia das Analogias & Custos:** Veja a análise aprofundada de custos (o caso do Consultor em Genebra) e o detalhamento de cada analogia prática em [**`docs/concepts.md`**](docs/concepts.md).

---

## 👥 O Conselho de Agentes: A Mente Sintética do Visão (*Vision Quest Protocol*)

<div align="center">
  <img src="assets/vision_quest_diorama.jpg" alt="A Mente Sintética do Visão - Vision Quest Diorama" width="100%" style="border-radius: 12px; margin: 20px 0;" />
  <p><em>Inspirado na icônica arte conceitual da série <strong>Vision Quest</strong>: sobre o platô craniano do White Vision com circuitos gravados, o sintozóide lê o periódico "SINGULARITY TODAY" em sua poltrona amarela enquanto o próprio <strong>Ultron</strong>, em casaco de veludo, pinta no cavalete o diagrama 3D da curvatura espaço-temporal da Singularidade Gravitacional (Event Horizon).</em></p>
</div>

Em vez de delegar todo o trabalho para um único modelo generalista inflado, o sistema opera como a **mente sintética do Visão**: uma banca deliberativa de 5 papéis neurais assimétricos em hardware local Apple Silicon:

| Agente / Papel | Modelo Local / Nuvem | Função Estrutural no Chassi Neural | Custo Cloud |
| :--- | :---: | :--- | :---: |
| **1. O Orquestrador (Mente)** | `Gemini Pro` | *Aura Branca/Dourada:* Decomposição macro e invariantes de sistema | Base ($1.50/M) |
| **2. O Construtor (Builder)** | `qwen2.5-coder:7b` | *Aura Verde Esmeralda:* Type-driven synthesis e patches cirúrgicos a ~40 tok/s | **$0.00** |
| **3. O Auditor (Skeptic)** | `deepseek-r1:1.5b` | *Aura Púrpura:* Red-team adversarial pré-disco (análise de nulos e tipos) | **$0.00** |
| **4. O Explorador (Scout)** | `nomic-embed-text` | *Aura Ciano:* Navegação em grafo vetorial de 768 dimensões (<15ms) | **$0.00** |
| **5. O Escriba (Distiller)** | `hermes3:3b` | *Aura Âmbar:* Compressão epistêmica BDI (histórico destilado para <500 tokens) | **$0.00** |

> 👥 **Guia Completo Vision Quest:** Veja o estudo aprofundado dos paradigmas teóricos (YAGNI, Red-Teaming, BDI), diagrama de sequência das 6 fases e a dinâmica adversarial completa em [**`docs/vision_quest.md`**](docs/vision_quest.md).

---

## 🧠 Matriz de Modelos Locais no Apple Silicon

Transformamos um **MacBook Air de 16GB de RAM** em uma estação de trabalho agêntica autônoma sem estourar a memória unificada nem depender de APIs pagas para tarefas mecânicas:

* **Trindade Co-residente Ativa:** `smollm2:1.7b` (Micro-Worker ~1.0 GB) + `deepseek-r1:1.5b` (Skeptic ~1.1 GB) + `qwen2.5-coder:7b` (Builder ~4.7 GB) mantidos simultaneamente na Metal GPU com `keep_alive: -1`.
* **Orçamento de VRAM Respeitado:** ~6.8 GB ativos, preservando mais de 9 GB de RAM livres para o macOS e o Antigravity IDE.
* **Velocidade de Execução Metal:** Inferências de micro-tarefas a **>120 tokens/s** e refatorações complexas a **~38 tokens/s**.

```mermaid
xychart-beta
    title "Pegada de Memória Unificada dos Modelos Locais (VRAM em GB)"
    x-axis ["nomic-embed", "mau-c", "deepseek-1.5b", "llama-1b", "granite-2b", "smollm-1.7b", "qwen-3b", "hermes-3b", "qwen-7b"]
    y-axis "VRAM (GB)" 0 --> 5
    bar [0.27, 0.41, 1.10, 1.23, 1.60, 1.70, 1.88, 2.00, 4.70]
```

> 📖 **Guia Completo dos Modelos:** Para o dicionário operacional dos 12 modelos, gráficos de velocidade de geração contínua (tok/s), lições de arquitetura e análise comparativa CPython vs Cython, consulte **[docs/models.md](docs/models.md)**.

---

## ⚙️ A Anatomia da Máquina: Centrífuga Gravitacional de Tokens

> *"O objeto é a explicação."* Seguindo a disciplina da skill **Anatomy**, a arquitetura de otimização de tokens não é apenas um conceito abstrato de software, mas opera analogamente a uma **máquina física de calibração laboratorial de precisão**.

<div align="center">
  <img src="assets/gravitational_token_centrifuge_rig.jpg" alt="Centrífuga Gravitacional de Tokens - Anatomy Rig" width="100%" style="border-radius: 12px; margin: 20px 0;" />
  <p><em>Figura 1.0 (Anatomy Spec): Bancada isométrica de alta precisão com câmara de vórtice em vidro de borossilicato, manômetros calibrados (8.6x redução, 0.26ms latência, 4.7GB VRAM) e tubulação de bypass de AST.</em></p>
  <p><a href="docs/anatomy/singularity_centrifuge.html"><strong>[Abrir Figura Interativa em SVG / HTML]</strong></a></p>
</div>

### Mapeamento dos Componentes Mecânicos:
* **Base de Ferro Fundido & Pés de Latão Serrilhados:** A infraestrutura de hardware Apple Silicon (MacBook Air M-Series, 16GB RAM) proporcionando sustentação estável sem vibrações térmicas ou swap no SSD.
* **Câmara Cilíndrica de Vidro de Borossilicato:** O vórtice central da Singularidade Gravitacional, onde o código bruto sofre aceleração centrífuga, forçando o ruído imperativo para as bordas e concentrando a essência sintática no núcleo.
* **Manômetro de Redução (8.6x / 88.5%):** Monitora a taxa de compressão entre os tokens projetados (76M) e os tokens efetivamente pagos (8.8M).
* **Mostrador Micrométrico de Latência (0.26 ms):** Aferição do tempo de resposta do guardrail `hook_pre_tool.py` validando patches na memória RAM antes de tocar o sistema de arquivos.
* **Coluna de Nível de Mercúrio (VRAM 4.7 GB):** O reservatório calibrado de Memória Unificada ocupado pelo modelo `qwen2.5-coder:7b`, preservando mais de 11 GB de RAM livres.
* **Conduítes e Tubos de Cobre de Bypass:** As rotas diretas de offload do `local-llm-mcp` que desviam micro-tarefas (regex, linter, JSON) para os modelos locais a ~40 tokens/s.

---

## 🗺️ Mapa das Camadas de Ação Agêntica (Draw.io)

<p align="center">
  <img src="assets/agentic_layers.svg" alt="Event Horizon - Camadas de Ação Agêntica" width="100%" />
</p>

> Fonte editável: [`docs/diagrams/agentic_layers.drawio`](docs/diagrams/agentic_layers.drawio) (abra no [app.diagrams.net](https://app.diagrams.net) ou na extensão Draw.io do VS Code). A imagem e o `.drawio` são gerados a partir do **mesmo layout** por [`generate_agentic_layers.py`](docs/diagrams/generate_agentic_layers.py) — para atualizar: `python3 docs/diagrams/generate_agentic_layers.py`.

| Camada | Escopo | Componente Principal | Papel no Pipeline |
| :--- | :--- | :--- | :--- |
| **Camada 1** | Entrada & Orquestração | Gemini Pro / Flash | Planejamento macro, emissão de tool calls e fixação de invariantes |
| **Camada 2** | Interceptação PreTool | `hook_pre_tool.py` / `GuardrailInterceptor` | Validação in-memory AST (<0.26ms), bloqueio destrutivo e reescrita de testes |
| **Camada 3** | Roteamento Cognitivo | `CognitiveArbiter` / `CircuitBreaker` | Classificação Sistema 1 vs 2 (McCabe > 10) e teto adaptativo de 8k tokens |
| **Camada 4** | Execução Local Tier 0 | `UnifiedExecutionPipeline` / `local-llm-mcp` | Drafter 7B + Skeptic 1.5B com zero tokens de nuvem |
| **Camada 5** | Memória & Cache Epistêmico | L1 RAM + L2 SQLite WAL + L3 Git Index | Poda diferencial (>96%), Merkle O(1) e persistência cross-session |
| **Camada 6** | Hardware & Apple Silicon | Ollama Metal GPU (<7.0 GB VRAM) | Co-residência tripla (`keep_alive: -1`) e KV-cache zero-prefill (`num_keep`) |

> 🏛️ **Detalhamento das Camadas:** Veja o funcionamento interno, o fluxo passo a passo de uma edição e as regras de segurança em [**`docs/architecture.md#4-dissecação-das-6-camadas-de-ação-agêntica`**](docs/architecture.md#4-dissecação-das-6-camadas-de-ação-agêntica).

---

## 🔬 As 20 Abstrações Arquiteturais do Sistema

O Event Horizon opera sob **20 abstrações de engenharia desacopladas** em Arquitetura Hexagonal, com foco em contenção de contexto, execução local Tier-0 e proteção do sistema de arquivos:

| # | Abstração | Componente Principal | Objetivo Central |
| :-: | :--- | :--- | :--- |
| **1** | **Guardrail In-Memory** | `hook_pre_tool.py` | Valida sintaxe AST em RAM (<0.05ms) antes de tocar o SSD; bloqueia erros sintáticos na origem. |
| **2** | **Poda Sintática de Contexto** | `CodeSkeletonizer` (`ast-search`) | Poda corpos de funções substituindo por `...`, reduzindo tokens em até 85%. |
| **3** | **RAG Semântico Local** | `SemanticRetriever` (`code-rag`) | Chunks por nó AST + embeddings `nomic-embed-text` com cache SHA-256 no Mac. |
| **4** | **Orquestração Cognitiva** | `cognitive-meta-router` | Enforça Plan-and-Solve (PS), Self-Refine (SR) e Subagent Token Budgeting (STB). |
| **5** | **Destilação Epistêmica** | `EpistemicDistiller` (`session-distiller`) | Converte históricos de +2M tokens em resumos de estado de <500 tokens (`session_state.md`). |
| **6** | **Ponytail Patching** | `replace_file_content` | Proíbe regravações de arquivos inteiros; enforça patches cirúrgicos de 5 a 15 linhas. |
| **7** | **Truncador RTK v2** | `rtk` (Real-Time Token Killer) | Trunca comandos de terminal verbosos no hook, retendo apenas o miolo relevante (-85% tokens). |
| **8** | **Local-First Draft** | `SpeculativeDrafter` (`local_draft_patch`) | Rascunho especulativo no `qwen 7B` local com validação AST e 1 auto-correção ($0.00). |
| **9** | **Storytelling & Telemetria 360** | `TelemetryAggregator` (:7890) | Converte métricas brutas em metáforas cognitivas (Livros Poupados, Cafés e Zero Retrabalho). |
| **10** | **Roteamento Dinâmico Cloud** | Matriz Gemini 2.0 | `flash_lite` ($0.075/M) para linter, `flash` ($0.10/M) para pesquisa e `pro` ($1.50/M) para orquestração. |
| **11** | **Pipeline dos 5 Nós** | Jornada da Requisição | Entrada Bruta ➔ Roteador ➔ Poda AST/RAG ➔ Execução Estratificada ➔ Guardrail & Git. |
| **12** | **Auto-Esqueleto em `view_file`** | `GuardrailInterceptor` | Bloqueia leituras cegas de arquivos >120 linhas sem fatia, forçando inspeção cirúrgica. |
| **13** | **Cognição Dual (Sistema 1 vs 2)** | `CognitiveArbiter` & `CircuitBreaker` | Sistema 1 (Local, <100ms, $0) vs Sistema 2 (Nuvem, Budget Envelope) com circuit breaker. |
| **14** | **Cache Epistêmico L1/L2** | `SqliteEpistemicCacheAdapter` | L1 RAM LRU (<0.05ms) + L2 SQLite WAL persistente com chave tripla imutável. |
| **15** | **Poda Dinâmica de Contexto** | `EpistemicContextSqueezer` | Projeção virtual em RAM sob teto de 8k tokens preservando os 2 turnos mais recentes. |
| **16** | **Pré-Fetching Preditivo** | `PredictivePreWarmer` | Thread background que pré-calcula o esqueleto AST no momento do `save` (0.00ms na tool call). |
| **17** | **Reflexão Adversarial Local** | `AdversarialReflector` | Builder (`qwen 7B`) vs Skeptic (`deepseek-r1 1.5B`) em RAM com 1 rodada de auto-refino ($0.00). |
| **18** | **Cascata Hierárquica Tier-0** | `HierarchicalCascade` | Micro-tarefas no `smollm2:1.7b` (>120 tok/s) com promoção silenciosa para o `qwen 7B` se a AST falhar. |
| **19** | **AST Merkle Tree Engine** | `AstMerkleEngine` | Invalidação granular O(1) por símbolo e montagem compositiva virtual do esqueleto (<0.01ms). |
| **20** | **VRAM Co-Residence & KV-Cache** | `InferenceOptimizer` | Co-residência tripla (6.8 GB VRAM) com `keep_alive: -1` e reuso de KV-cache via `num_keep`. |

> 🔬 **Documentação Técnica Aprofundada:** Para a análise completa de cada abstração (Problema Fundamental, Como Funciona e Por Que Funciona), consulte **[docs/abstractions.md](docs/abstractions.md)**.

---

## 🏗️ Árvore de Diretórios do Projeto (Sanitizada para GitHub)

```
.
├── assets/
│   ├── agentic_layers.svg           # Mapa das 6 camadas de ação agêntica (gerado do .drawio)
│   └── cyberpunk_singularity.jpg    # Arte visual cyberpunk da singularidade gravitacional
├── docs/diagrams/
│   ├── agentic_layers.drawio        # Fonte editável do mapa de camadas
│   └── generate_agentic_layers.py   # Gera .drawio + .svg a partir de um único layout
├── src/                             # ARQUITETURA HEXAGONAL & SOLID (Zero Dependências Externas)
│   ├── domain/                      # Regras de Negócio Puras (Entities, Value Objects, Exceptions)
│   │   ├── entities.py              # SessionState, CodeChunk, TelemetrySnapshot, StorytellingMetrics
│   │   ├── value_objects.py         # TokenCount, CostUSD, DiffPatch, ModelTier, CacheKey, CacheEntry
│   │   └── exceptions.py            # SyntaxValidationError, PatchApplicationError, ModelInferenceError
│   ├── ports/                       # Contratos Abstratos Estritos (typing.Protocol / ABC)
│   │   ├── inbound/                 # Driving Ports (IGuardrail, ICognitiveArbiter, ICircuitBreaker, IEpistemicMemoizer, IContextSqueezer, IPreWarmer, IAdversarialReflector, IHierarchicalCascade, IAstMerkleEngine, IInferenceOptimizer)
│   │   └── outbound/                # Driven Ports (ILLMClient, IAstParser, IEpistemicCache, IVectorStore)
│   ├── application/                 # Casos de Uso Desacoplados (Orquestração do Domínio e Portas)
│   │   ├── guardrail_interceptor.py # Interceptação PreToolUse e validação in-memory
│   │   ├── code_skeletonizer.py     # Poda sintática com retenção de contratos
│   │   ├── cognitive_arbiter.py     # Árbitro heurístico-semântico (<2ms, $0) Sistema 1 vs 2
│   │   ├── escalation_circuit_breaker.py # Trava contra loops de erro com síntese de handoff
│   │   ├── epistemic_memoizer.py    # Decorator/Orquestrador de memoização com chave tripla
│   │   ├── epistemic_context_squeezer.py # Poda virtual in-memory sob teto adaptativo de 8k
│   │   ├── predictive_pre_warmer.py # Watcher assíncrono e pré-aquecimento de AST em RAM
│   │   ├── adversarial_reflector.py # Loop reflexivo Builder vs Skeptic com auto-cura em RAM
│   │   ├── hierarchical_cascade.py  # Cascata hierárquica smollm2 (120 t/s) com promoção para 7B
│   │   ├── ast_merkle_engine.py     # Decomposição Merkle Tree e montagem compositiva virtual
│   │   ├── inference_optimizer.py   # Orquestração VRAM co-residente e KV-cache zero-prefill
│   │   ├── semantic_retriever.py    # RAG local via AST chunking e similaridade de cosseno
│   │   ├── speculative_drafter.py   # Draft local 7B com 1-shot self-refine retry
│   │   ├── epistemic_distiller.py   # Destilação de sessões para markdown persistente
│   │   └── telemetry_aggregator.py  # Agregação 360, matriz de provedores e storytelling
│   └── adapters/                    # Implementações Técnicas Concretas (Plugs)
│       ├── inbound/                 # Drivers (hook_adapter, mcp_adapter, http_telemetry_adapter, cli)
│       └── outbound/                # Driven (ollama, python_ast, sqlite_epistemic_cache, file_cache)
├── scripts/                         # FACHADAS FINAS DE RETROCOMPATIBILIDADE (<15 linhas)
│   ├── hook_pre_tool.py             # -> src.adapters.inbound.hook_adapter (Fallback à prova de falhas)
│   ├── local_llm_mcp.py             # -> src.adapters.inbound.mcp_adapter (Stdio JSON-RPC v2)
│   ├── token_tracker_server.py      # -> src.adapters.inbound.http_telemetry_adapter (:7890)
│   ├── code_rag.py                  # -> src.adapters.inbound.cli_adapters (CLI RAG)
│   ├── session_distiller.py         # -> src.adapters.inbound.cli_adapters (CLI Distiller)
│   └── rtk                          # Truncador dinâmico de saída de terminal
├── tests/
│   ├── unit/                        # Testes Unitários de Domínio e Casos de Uso com Fakes Puros
│   │   ├── test_domain.py           # Validação de invariantes, conversão de tokens/café
│   │   ├── test_use_cases.py        # Validação de guardrails, arbiter, circuit breaker e drafter
│   │   ├── test_epistemic_cache.py  # Validação de L1 RAM, L2 SQLite WAL e invalidação determinística
│   │   ├── test_context_squeezer.py # Validação de poda 3-níveis e teto adaptativo de 8k tokens
│   │   ├── test_pre_warmer.py       # Validação de detecção de mtime e aquecimento preditivo L1/L2
│   │   ├── test_adversarial_reflector.py # Validação do loop reflexivo Builder vs Skeptic em RAM
│   │   ├── test_hierarchical_cascade.py  # Validação de cascata smollm2 1.7B e promoção silenciosa
│   │   ├── test_ast_merkle_engine.py     # Decomposição hierárquica e invalidação O(1) Merkle Tree
│   │   └── test_inference_optimizer.py   # Validação de co-residência VRAM e reuso KV-cache
│   ├── integration/                 # Testes de Integração de Adaptadores Reais
│   │   └── test_adapters.py         # Teste real de AST Python/JSON e FileSystem
│   └── benchmark_skills.py          # Suíte E2E de validação e medição de redução de tokens (25 assertions)
├── AGENTS.md                        # Regras locais do repositório (Event Horizon)
├── architecture.drawio              # Diagrama nativo editável no Draw.io / diagrams.net
└── README.md
```

---

## 🏛️ Arquitetura Hexagonal (Ports & Adapters) & Princípios SOLID

O núcleo de engenharia do Gravitational Singularity opera estritamente sob **Arquitetura Hexagonal (Ports & Adapters)** com **Zero Dependências Externas** (utilizando exclusivamente a biblioteca padrão do Python 3.10+: `typing.Protocol`, `dataclasses`, `abc`, `ast`, `urllib`, `json`), garantindo inicialização a frio em **<0.26ms** sem overhead de `pip` ou ambientes virtuais pesados.

```
                   ┌────────────────────────────────────────┐
                   │          DRIVING ADAPTERS              │
                   │  • Antigravity PreTool Hook (stdin)   │
                   │  • Local LLM MCP Server (stdio RPC)    │
                   │  • Telemetry Daemon HTTP (:7890)       │
                   └──────────────────┬─────────────────────┘
                                      │ (invoca)
                                      ▼
                   ┌────────────────────────────────────────┐
                   │             INBOUND PORTS              │
                   │  IGuardrailService, ILocalDraftService │
                   │  ISyntaxCompressor, ITelemetryService  │
                   └──────────────────┬─────────────────────┘
                                      │
                                      ▼
        ┌──────────────────────────────────────────────────────────────┐
        │                       APPLICATION CORE                       │
        │  GuardrailInterceptor, SpeculativeDrafter, CodeSkeletonizer  │
        │  SemanticRetriever, EpistemicDistiller, TelemetryAggregator  │
        │                                                              │
        │                      DOMAIN ENTITIES                         │
        │   TokenMetric, CostUSD, DiffPatch, SessionState, CodeChunk   │
        └─────────────────────────────┬────────────────────────────────┘
                                      │
                                      ▼
                   ┌────────────────────────────────────────┐
                   │             OUTBOUND PORTS             │
                   │  ILLMClient, IAstParser, IVectorStore  │
                   │  ITranscriptRepository, IFileSystem    │
                   └──────────────────┬─────────────────────┘
                                      │ (implementado por)
                                      ▼
                   ┌────────────────────────────────────────┐
                   │           DRIVEN ADAPTERS              │
                   │  • OllamaClientAdapter (Metal API)     │
                   │  • MultiLanguageAstAdapter (ast.parse) │
                   │  • JsonFileCacheAdapter (SHA-256)      │
                   │  • FileTranscriptRepository            │
                   └────────────────────────────────────────┘
```


> 📖 **Guia Completo da Arquitetura & SOLID:** Veja o detalhamento completo dos 5 princípios SOLID, portas inbound/outbound, fachadas finas de retrocompatibilidade e diagrama de camadas Mermaid em [**`docs/architecture.md`**](docs/architecture.md).

---

## 📊 Dashboard de Telemetria 360 & Storytelling (`http://127.0.0.1:7890`)

O servidor de telemetria opera como um daemon HTTP/JSON em background escaneando continuamente os logs de execução do Antigravity. Ele provê métricas ao vivo, alternância de visão entre **Sessão Ativa** e **Histórico Global**, e dois modos de visualização: **Modo Engenharia** e **Modo Storytelling (Leigo)**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               ANTIGRAVITY TELEMETRY & EFFICIENCY MATRIX v2 (PAINEL 360)                │
├────────────────────────────────┬───────────────────────────────┬───────────────────────┤
│ REDUÇÃO CONSOLIDADA            │ TAXA DE EFICIÊNCIA GLOBAL     │ ECONOMIA FINANCEIRA   │
│ 8.4x Menos Tokens Consumidos   │ 88.1% Eficiência (85.9% Sess) │ $100.76 USD Salvos    │
├────────────────────────────────┴───────────────────────────────┴───────────────────────┤
│ STORYTELLING & METÁFORAS HUMANAS PARA LEIGOS                                           │
│ 📚 Livros Poupados:         ~269 livros inteiros de 300 páginas processados a custo zero│
│ ☕ Dinheiro Real Poupado:    R$ 564.26 poupados na fatura da API (~47 cafés especiais) │
│ 🛡️ Zero Retrabalho:         42 quebras de sintaxe barradas na RAM antes de tocar o SSD │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ SIMULADOR MULTI-PROVEDOR (CUSTO PROJETADO SEM SUITE vs. NET REAL PAGO)                │
│ • OpenAI GPT-4o               : Sem Suite $276.26 │ Com Suite $32.75 (Poupado: +$243.51)│
│ • Anthropic Claude 3.5 Sonnet : Sem Suite $365.80 │ Com Suite $43.36 (Poupado: +$322.44)│
│ • Google Gemini 2.0 (Base)    : Sem Suite $114.31 │ Com Suite $13.55 (Poupado: +$100.76)│
│ ⚡ NET REAL PAGO (SINGULARITY) : $13.55 USD (ECONOMIA LÍQUIDA REAL: +$100.76 USD)      │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ MATRIZ DE ROTEAMENTO DINÂMICO GEMINI EM NUVEM                                         │
│ • Gemini 2.0 Flash-Lite : $0.075 / 1M (-95% vs Pro) │ Micro-validações, lint e checks  │
│ • Gemini 2.0 Flash      : $0.100 / 1M (-93% vs Pro) │ Pesquisa ampla e subagentes      │
│ • Gemini 2.0 Pro        : $1.500 / 1M (Base)        │ Orquestrador e arquitetura macro │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 A Jornada de Uma Chamada: Do Prompt aos Modelos e Entrega

A arquitetura opera em um pipeline de 5 fases interativas para garantir que cada token gasto gere o máximo retorno de engenharia:

```mermaid
flowchart LR
    A["1. Entrada Bruta<br/>(Prompt do Engenheiro)"] --> B["2. Roteador Gravitacional<br/>(Cognitive Meta-Router)"]
    B --> C["3. Poda AST & Scout RAG<br/>(nomic-embed + ast-search)"]
    C --> D{"4. Execução Estratificada"}
    D -->|Micro-Refactor| D1["Tier 0: Qwen 7B Local<br/>($0.00 / Zero-Cloud)"]
    D -->|Pesquisa / Subagente| D2["Tier 1-2: Gemini Flash<br/>($0.075 - $0.10 / 1M)"]
    D -->|Arquitetura Macro| D3["Tier 3: Gemini Pro<br/>($1.50 / 1M)"]
    D1 --> E["5. Guardrail In-Memory & Git<br/>(hook_pre_tool + RTK)"]
    D2 --> E
    D3 --> E
```

1. **1. Entrada Bruta:** A requisição chega com histórico e contexto do repositório (~50k tokens brutos).
2. **2. Roteador Gravitacional:** O `cognitive-meta-router` analisa a complexidade e decide a rota de menor custo.
3. **3. Poda AST & Scout RAG:** O `ast-search` elimina 70% das funções imperativas e o `code-rag` puxa apenas os blocos relevantes via embeddings locais.
4. **4. Execução Estratificada:**
   - Patches pontuais são delegados ao **`qwen2.5-coder:7b`** via `local_draft_patch` (**Custo = $0.00**).
   - Subagentes exploratórios de pesquisa concorrente rodam em **Gemini Flash / Flash-Lite** (**Economia de até 95%**).
   - O orquestrador central reserva o **Gemini Pro** exclusivamente para decisões estruturais.
5. **5. Guardrail In-Memory & Git:** O `hook_pre_tool.py` compila o patch em 0.26ms na memória RAM. Se for válido, aplica diff cirúrgico; o `rtk` suprime ruídos de terminal e grava a entrega limpa no Git.

---

## 🎨 Diagrama Editável no Draw.io

O projeto acompanha o arquivo vetorial completo [architecture.drawio](architecture.drawio) contendo todas as 5 camadas, estilização GitHub Dark e conexões lógicas, pronto para ser aberto diretamente no [app.diagrams.net](https://app.diagrams.net) ou na extensão Draw.io do VS Code.

O mapa atualizado das **6 camadas de ação agêntica** (com status ATIVO/BIBLIOTECA de cada componente) está em [docs/diagrams/agentic_layers.drawio](docs/diagrams/agentic_layers.drawio), renderizado em [assets/agentic_layers.svg](assets/agentic_layers.svg) — veja a seção *🗺️ Mapa das Camadas de Ação Agêntica* acima.

---

## 📈 Resultados dos Benchmarks Quantitativos & Testes

Validação quantitativa contínua aferindo taxa de compressão de tokens, latência de barramento e integridade do código:

| Vetor de Medição | Métrica Obtida | Referência / Impacto | Status |
| :--- | :---: | :--- | :---: |
| **Poda de Tokens AST (`ast-search`)** | **68.2% redução** | Esqueletos Python e TypeScript 100% compiláveis | ✅ PASS |
| **Poda Diferencial Merkle Tree** | **>96.0% redução** | Envia apenas nó alterado e método alvo via hash O(1) | ✅ PASS |
| **IPC Zero-Copy (`SharedMemoryRingBuffer`)** | **<5 µs** | Comunicação inter-processos sem loopback HTTP/TCP | ✅ PASS |
| **Latência do Guardrail In-Memory** | **0.26 ms** | Validação sintática instantânea antes de gravar em disco | ✅ PASS |
| **Smart Error Slicing (Tracebacks)** | **<80 tokens** | Isola asserção e linha de erro; elimina ruídos de frameworks | ✅ PASS |
| **Inferência Local (`smollm2:1.7b`)** | **~120-130 tok/s** | Resolução em sub-segundo de micro-tarefas e tipagem | ✅ PASS |
| **Inferência Local (`qwen2.5-coder:7b`)** | **~35-40 tok/s** | Raciocínio profundo e patches complexos a custo zero | ✅ PASS |
| **Suíte de Testes Automatizada** | **63/63 unit tests** | Executados em **0.333s** com zero dependências externas | ✅ PASS |
| **Benchmark E2E de Compressão** | **25/25 assertions** | Verificação end-to-end do pipeline de compressão | ✅ PASS |

> 📖 **Relatório Completo de Benchmarks:** Veja tabelas detalhadas por linguagem, logs completos de execução dos 63 testes unitários e instruções passo a passo para reprodução em [**`docs/benchmarks.md`**](docs/benchmarks.md).

---

## 🚀 Como Replicar no seu Mac (Setup em 5 Minutos)

1. **Baixar os Modelos Locais no Ollama (Aceleração Metal Apple Silicon):**
   ```bash
   ollama pull nomic-embed-text    # 274MB - RAG semântico local
   ollama pull deepseek-r1:1.5b    # 1.1GB - Raciocínio rápido e JSON
   ollama pull qwen2.5-coder:3b    # 1.9GB - Boilerplate mecânico
   ollama pull qwen2.5-coder:7b    # 4.7GB - Speculative local drafts (Zero-Cloud)
   ollama pull deepseek-r1:7b      # 4.9GB - Auditor cético profundo
   ollama pull hermes3:3b          # 2.0GB - Destilação epistêmica
   ```

2. **Vincular o Módulo Hexagonal ao Antigravity:**
   ```bash
   ln -sf $(pwd)/src ~/.gemini/config/src
   ```

3. **Registrar o Servidor MCP no Antigravity (`~/.gemini/config/mcp_config.json`):**
   ```json
   {
     "mcpServers": {
       "local-llm-mcp": {
         "command": "python3",
         "args": ["/Users/mauriciohelfstein/dev/gravitational-singularity/scripts/local_llm_mcp.py"]
       }
     }
   }
   ```

4. **Ativar o Guardrail Pre-Tool com Validador AST em RAM (`~/.gemini/config/hooks.json`):**
   ```json
   {
     "event-horizon-gate": {
       "enabled": true,
       "PreToolUse": [
         {
           "matcher": "run_command|view_file|replace_file_content|write_to_file",
           "hooks": [
             {
               "type": "command",
               "command": "/Users/mauriciohelfstein/dev/gravitational-singularity/scripts/hook_pre_tool.py",
               "timeout": 10
             }
           ]
         }
       }
     }
   }
   ```

5. **Iniciar a Telemetria 360 em Background:**
   ```bash
   python3 scripts/token_tracker_server.py start
   # Acesse no navegador: http://127.0.0.1:7890
   ```
