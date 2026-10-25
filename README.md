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
| 👥 **[Protocolo Vision Quest](docs/vision_quest.md)** | Mente sintética & Conselho de Agentes | Arte conceitual Vision Quest, papéis assimétricos e fluxo operacional |
| 🏛️ **[Arquitetura Hexagonal & SOLID](docs/architecture.md)** | Design de software e fluxo E2E | Ports & Adapters, SOLID, pipeline de execução e diagramas de arquitetura |
| 📈 **[Resultados & Benchmarks](docs/benchmarks.md)** | Dados quantitativos e suíte de testes | 142 testes automatizados (100% PASS), 25 asserções quantitativas e latências |
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

## 🏛️ Arquitetura da Solução & Fluxo Agêntico de Ponta a Ponta (E2E)

<div align="center">
  <a href="assets/solution_architecture.svg">
    <img src="assets/solution_architecture.png" alt="Arquitetura de Execução Agêntica do Event Horizon - Pipeline E2E" width="100%" style="border-radius: 12px; margin: 20px 0; border: 1px solid #30363d;" />
  </a>
  <p><em>Figura 1: Arquitetura completa da solução — Do prompt à gravação em disco: interceptação em RAM (&lt;0.26ms), roteamento cognitivo Sistema 1 vs 2, execução local Tier 0 ($0 nuvem), compressão AST/Merkle e persistência segura no Apple Silicon. [<a href="assets/solution_architecture.svg">Abrir SVG Vetorial em Alta Resolução</a>]</em></p>
</div>

---

## 👥 O Conselho de Agentes: Papéis Neurais Assimétricos

Em vez de delegar todo o trabalho para um único modelo generalista inflado, o sistema opera como a **mente sintética do Visão**: uma banca deliberativa de 5 papéis neurais assimétricos em hardware local Apple Silicon:

| Agente / Papel | Modelo Local / Nuvem | Função Estrutural no Chassi Neural | Custo Cloud |
| :--- | :---: | :--- | :---: |
| **1. O Orquestrador (Mente)** | `Gemini Pro` | *Aura Branca/Dourada:* Decomposição macro e invariantes de sistema | Base ($1.50/M) |
| **2. O Construtor (Builder)** | `qwen2.5-coder:7b` | *Aura Verde Esmeralda:* Type-driven synthesis e patches cirúrgicos a ~21 tok/s | **$0.00** |
| **3. O Auditor (Skeptic)** | `deepseek-r1:1.5b` | *Aura Púrpura:* Red-team adversarial pré-disco a ~78 tok/s (TTFT 49.8ms) | **$0.00** |
| **4. O Explorador (Scout)** | `nomic-embed-text` | *Aura Ciano:* Navegação em grafo vetorial de 768 dimensões (<15ms) | **$0.00** |
| **5. O Escriba (Distiller)** | `hermes3:3b` | *Aura Âmbar:* Compressão epistêmica BDI (histórico destilado para <500 tokens) | **$0.00** |

> 👥 **Guia Completo Vision Quest:** Veja o estudo aprofundado dos paradigmas teóricos (YAGNI, Red-Teaming, BDI), diagrama de sequência das 6 fases e a dinâmica adversarial completa em [**`docs/vision_quest.md`**](docs/vision_quest.md).

---

## 🧠 Matriz de Modelos Locais no Apple Silicon

Transformamos um **MacBook Air/Pro de 16GB de RAM** em uma estação de trabalho agêntica autônoma sem estourar a memória unificada nem depender de APIs pagas para tarefas mecânicas:

* **Trindade Co-residente Ativa:** `smollm2:1.7b` (Micro-Worker ~0.98 GB) + `deepseek-r1:1.5b` (Skeptic ~0.91 GB) + `qwen2.5-coder:7b` (Builder ~4.43 GB) mantidos simultaneamente na Metal GPU com `keep_alive: -1`.
* **Orçamento de VRAM Respeitado:** ~6.8 GB ativos, preservando mais de 9 GB de RAM livres para o macOS e o Antigravity IDE.
* **Velocidade de Execução Metal (Medida no M4):** Inferências de micro-tarefas a **50-78 tokens/s** e refatorações complexas de 7B a **~21 tokens/s**.

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

## 🔬 Os Pilares de Produção do Sistema (Hexagonal Core)

O Event Horizon opera sob uma **Arquitetura Hexagonal em Python stdlib** estrita, eliminando dependências externas e concentrando a execução em 6 pilares de produção verificados:

| Pilar | Componente Principal | O Que Faz em Produção | Eficiência Comprovada |
| :--- | :--- | :--- | :---: |
| **1. Guardrail In-Memory** | `hook_pre_tool.py` / `GuardrailInterceptor` | Valida sintaxe AST (Python, TypeScript) e integridade JSON em RAM antes de tocar o SSD. Bloqueia comandos destrutivos. | **<0.26 ms** de latência |
| **2. Poda Sintática AST** | `CodeSkeletonizer` (`ast-search`) | Poda corpos imperativos mantendo assinaturas, tipos, contratos e interfaces em Python e TypeScript. | **68.2%** menos tokens |
| **3. Merkle Tree Diferencial** | `AstMerkleEngine` | Decomposição criptográfica por símbolo. Poda irmãos não alterados e envia apenas o símbolo-alvo com hash O(1). | **91.3%** menos tokens |
| **4. Patches Cirúrgicos Ponytail** | `replace_file_content` | Proíbe regravações de arquivos inteiros; enforça substituições pontuais com validação prévia. | **Zero** retrabalho de diff |
| **5. Tríade Local Co-Residente** | `qwen2.5-coder:7b` + `deepseek-r1:1.5b` + `smollm2:1.7b` | Execução local no Apple Silicon (Metal GPU) com `keep_alive: -1` para rascunhos, auditoria e micro-tarefas. | **$0.00** custo de nuvem |
| **6. Cache Epistêmico L0/L1/L2** | `SemanticPromptCache` / `SqliteEpistemicCacheAdapter` | L0 em RAM para invariantes conhecidos (0ms) + L1 LRU + L2 SQLite WAL persistente entre sessões. | **0 ms** em cache hit |

> 🔬 **Catálogo de Engenharia & Módulos Experimentais:** Para o detalhamento completo dos contratos e módulos da camada de pesquisa (IPC zero-copy, Metal batch cosine similarity e extensões), consulte **[docs/abstractions.md](docs/abstractions.md)**.

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
│   │   ├── telemetry_aggregator.py  # Agregação 360, matriz de provedores e storytelling
│   │   ├── asymmetric_speculative_decoder.py # Speculative decoding draft 1.7B + target 7B (>90 tok/s)
│   │   ├── semantic_prompt_cache.py # Cache semântico L0 com quantização escalar (0ms)
│   │   ├── agentic_self_healing_runner.py # Loop de auto-cura de testes em sandbox RAM ($0)
│   │   ├── bitnet_quantizer.py      # Quantização ternária {-1, 0, 1} BitNet b1.58 (14B em 2.4 GB)
│   │   ├── paged_attention_engine.py # Metal PagedAttention com prefix sharing e zero fragmentação
│   │   ├── tree_speculative_decoder.py # Especulação em árvore Medusa (>85% aceitação, >140 tok/s)
│   │   └── smt_formal_verification_gate.py # Provador de teoremas formais em RAM (<1ms)
│   ├── metal/                       # Metal Shading Language (MSL) Compute Kernels Nativo
│   │   └── batch_cosine.metal       # Compute shader SIMD 4x batch cosine similarity (<5µs)
│   └── adapters/                    # Implementações Técnicas Concretas (Plugs)
│       ├── inbound/                 # Drivers (hook_adapter, mcp_adapter, http_telemetry_adapter, cli)
│       └── outbound/                # Driven (metal_async_pipeline, metal_compute, incremental_ast, ollama, sqlite)
├── scripts/                         # FACHADAS FINAS DE RETROCOMPATIBILIDADE (<15 linhas)
│   ├── hook_pre_tool.py             # -> src.adapters.inbound.hook_adapter (Fallback à prova de falhas)
│   ├── local_llm_mcp.py             # -> src.adapters.inbound.mcp_adapter (Stdio JSON-RPC v2)
│   ├── token_tracker_server.py      # -> src.adapters.inbound.http_telemetry_adapter (:7890)
│   ├── code_rag.py                  # -> src.adapters.inbound.cli_adapters (CLI RAG)
│   ├── session_distiller.py         # -> src.adapters.inbound.cli_adapters (CLI Distiller)
│   └── rtk                          # Truncador dinâmico de saída de terminal
├── tests/
│   ├── conftest.py                  # Fixtures globais pytest, auto-marker e sanitização SHM
│   ├── unit/                        # Testes Unitários Granulares em Memória RAM
│   │   ├── domain/                  # Entidades, Value Objects e invariantes matemáticos
│   │   ├── application/             # Casos de uso, guardrails, cascata e drafters
│   │   └── frontier/                # BitNet, PagedAttention, SMT, IPC e JIT Shaders
│   ├── integration/                 # Testes de Integração (FS, SQLite, Mmap, Shared Memory)
│   ├── e2e/                         # Testes End-to-End (Council Dispatch & Full Pipeline)
│   └── benchmarks/                  # Suíte de Benchmarks Quantitativos e Redução de Tokens
├── pytest.ini                       # Configuração pytest com markers estritos (unit, integration, e2e, benchmark)
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

## 📊 Painel de Telemetria Operacional (`http://127.0.0.1:7890`)

O servidor de telemetria opera como um daemon HTTP/JSON em background escaneando continuamente os logs de execução do Antigravity e provendo métricas operacionais reais:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               ANTIGRAVITY TELEMETRY & EFFICIENCY MATRIX (PAINEL OPERACIONAL)           │
├────────────────────────────────┬───────────────────────────────┬───────────────────────┤
│ REDUÇÃO CONSOLIDADA            │ TAXA DE EFICIÊNCIA GLOBAL     │ ECONOMIA FINANCEIRA   │
│ 8.7x Menos Tokens em Trânsito  │ 88.5% Eficiência (85.9% Sess) │ $100.76 USD Salvos    │
├────────────────────────────────┴───────────────────────────────┴───────────────────────┤
│ TELEMETRIA DE EXECUÇÃO & LATÊNCIA                                                      │
│ • Poda Sintática AST           : 68.2% redução medida em Python / TypeScript           │
│ • Esqueleto Diferencial Merkle : 91.3% redução mantendo apenas símbolo-alvo            │
│ • Latência do Guardrail Hook   : <0.26 ms (In-Memory AST check antes de tocar o SSD)  │
│ • Retrabalho Evitado           : Quebras de sintaxe barradas na RAM antes de persistir │
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
| **Poda Diferencial Merkle Tree** | **91.3% redução** | Envia apenas nó alterado e método-alvo via hash O(1) | ✅ PASS |
| **IPC Zero-Copy (`SharedMemoryRingBuffer`)** | **<5 µs** | Comunicação inter-processos sem loopback HTTP/TCP | ✅ PASS |
| **Latência do Guardrail In-Memory** | **0.26 ms** | Validação sintática instantânea antes de gravar em disco | ✅ PASS |
| **Smart Error Slicing (Tracebacks)** | **<80 tokens** | Isola asserção e linha de erro; elimina ruídos de frameworks | ✅ PASS |
| **Inferência Local (`deepseek-r1:1.5b`)** | **77.7 tok/s (49.8ms TTFT)** | Auditor cético em RAM com raciocínio CoT e JSON estrito | ✅ PASS |
| **Inferência Local (`smollm2:1.7b`)** | **50.0 tok/s (50.6ms TTFT)** | Resolução rápida de micro-tarefas, tipagem e regex | ✅ PASS |
| **Inferência Local (`qwen2.5-coder:7b`)** | **20.8 tok/s (194ms TTFT)** | Raciocínio profundo e patches complexos a custo zero | ✅ PASS |
| **Suíte Granular Pytest & Unittest** | **142/142 tests** | Executados em **1.22s** (Unit Core/Frontier, Integration, E2E, Benchmarks) | ✅ PASS |
| **Benchmark E2E de Compressão** | **25/25 assertions** | Verificação quantitativa de redução AST (68.2%) | ✅ PASS |

> 📖 **Relatório Completo de Benchmarks:** Veja tabelas detalhadas por linguagem, logs completos de execução dos 142 testes automatizados e medições empíricas live do Ollama em [**`docs/benchmarks.md`**](docs/benchmarks.md).

---

## 🚀 Como Replicar no seu Mac (Setup em 5 Minutos)

1. **Baixar os Modelos da Tríade Local no Ollama (Aceleração Metal Apple Silicon):**
   ```bash
   ollama pull nomic-embed-text    # 274MB - RAG semântico e busca vetorial local
   ollama pull deepseek-r1:1.5b    # 1.1GB - Auditor cético pré-disco e raciocínio CoT
   ollama pull smollm2:1.7b        # 0.9GB - Micro-tarefas mecânicas de alta velocidade
   ollama pull qwen2.5-coder:7b    # 4.7GB - Construtor local de patches (Zero-Cloud)
   ```

2. **Rodar a Suíte Completa de Testes Granulares (Pytest):**
   ```bash
   pytest -v
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
           "matcher": "run_command|view_file|edit_file|write_file|replace_file_content|write_to_file",
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
