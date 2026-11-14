# 🏗️ Estrutura do Código & Mapeamento Hexagonal

> **Guia Arquitetural de Diretórios:** Mapeamento completo dos módulos, contratos e responsabilidades segundo os princípios de Clean Architecture e Ports & Adapters (Hexagonal Core).

---

## 🏛️ Árvore de Diretórios Sanitizada

```
.
├── assets/                          # Diagramas vetoriais SVG e arte do projeto
│   ├── agentic_layers.svg           # Mapa das 6 camadas de ação agêntica
│   ├── call_journey_pipeline.svg    # Pipeline visual de 5 estágios da chamada
│   ├── solution_architecture.svg    # Arquitetura hexagonal de ponta a ponta
│   └── vram_footprint.svg           # Gráfico vetorial de pegada de VRAM no M4
├── docs/                            # Documentação Técnica Especializada
│   ├── anatomy/                     # Anatomia física e especificação da centrífuga
│   ├── architecture.md              # Dissecação técnica de Ports & Adapters e SOLID
│   ├── architecture_patterns.md     # Padrões de mercado (FrugalGPT, RouteLLM, BNF)
│   ├── benchmarks.md                # Resultados empíricos e latências medidas
│   ├── codebase_structure.md        # Este guia estrutural de arquivos
│   ├── concepts.md                  # As 5 analogias práticas e análise de custos
│   ├── models.md                    # Dicionário dos modelos e performance Metal
│   ├── portability_matrix.md        # Matriz de compatibilidade multi-plataforma
│   ├── productization_and_holistic_guide.md # Roadmap de produto, OTel e MCP
│   └── vision_quest.md              # Conselho Neural e protocolo BDI
├── src/                             # NÚCLEO HEXAGONAL (Zero Dependências Externas)
│   ├── domain/                      # Entidades e Regras de Negócio Puras
│   │   ├── entities.py              # SessionState, CodeChunk, StorytellingMetrics
│   │   ├── exceptions.py            # SyntaxValidationError, PatchApplicationError
│   │   └── value_objects.py         # TokenCount, CostUSD, DiffPatch, ModelTier
│   ├── ports/                       # Interfaces e Contratos Abstratos Estritos
│   │   ├── inbound/                 # Driving Ports (Casos de uso e orquestradores)
│   │   │   ├── agent_governor_port.py   # IAgentGovernor (Teto 8.5GB VRAM)
│   │   │   ├── hybrid_routing_port.py   # IHybridRoutingEngine (Confiança/Entropia)
│   │   │   ├── hybrid_search_port.py    # IHybridSearchEngine (Fusão RRF)
│   │   │   ├── repo_map_port.py         # IRepoMapEngine (Personalized PageRank)
│   │   │   └── guardrail_port.py        # IGuardrail (Validação in-memory)
│   │   └── outbound/                # Driven Ports (Acesso a infraestrutura e hardware)
│   │       ├── llm_client_port.py       # ILLMClient
│   │       ├── ast_parser_port.py       # IAstParser
│   │       └── vector_store_port.py     # IVectorStore
│   ├── application/                 # Casos de Uso e Orquestradores
│   │   ├── dynamic_agent_governor.py    # Governança de VRAM e time-slicing
│   │   ├── hybrid_routing_engine.py     # Classificador de tarefas e roteamento
│   │   ├── hybrid_search_rrf.py         # RRF entre vetores BLAS e SQLite FTS5
│   │   ├── repo_map_pagerank_engine.py  # Grafo de contexto do repositório (<800 tok)
│   │   ├── swarm_orchestrator.py        # Orquestrador do enxame de agentes locais
│   │   ├── token_savings_estimator.py   # Calculadora de tokens poupados em tempo real
│   │   ├── guardrail_interceptor.py     # Interceptação em RAM (<0.26ms)
│   │   ├── code_skeletonizer.py         # Poda sintática AST (>68% economia)
│   │   └── ast_merkle_engine.py         # Decomposição Merkle Tree (>91% diff)
│   └── adapters/                    # Implementações Técnicas Concretas
│       ├── inbound/                 # Adaptadores de Entrada
│       │   ├── universal_mcp_server.py  # Servidor MCP Stdio JSON-RPC padrão
│       │   ├── doctor_cli.py            # CLI `singularity doctor` e `singularity mcp`
│       │   ├── cli_adapters.py          # Entrypoints de linha de comando
│       │   └── hook_adapter.py          # Interceptador pré-ferramenta do IDE
│       └── outbound/                # Adaptadores de Saída
│           ├── accelerate_vector_adapter.py # Apple Accelerate BLAS nativo
│           ├── grammar_decoding_adapter.py  # Decodificação restrita BNF
│           ├── opentelemetry_exporter.py    # Exportador OTel ResourceSpans
│           ├── ollama_adapter.py            # Conexão com Ollama Local Metal
│           └── sqlite_storage_adapter.py    # SQLite WAL persistente
├── scripts/                         # Fachadas e Automações
│   ├── hook_pre_tool.py             # Gancho de interceptação em runtime
│   ├── benchmark_live_ollama.py     # Medição real de latência e tokens/s
│   └── reachability.py              # Gate de arquitetura de 84 módulos
└── tests/                           # Suíte de Testes Automatizados (170 testes)
    ├── conftest.py                  # Fixtures e setup do ambiente
    ├── benchmark_skills.py          # 25 asserções quantitativas de tokens
    └── unit/                        # Testes unitários isolados em memória
        ├── domain/                  # Testes de invariantes de domínio
        ├── application/             # Testes de casos de uso e enxame
        └── frontier/                # Testes de aceleração de hardware e IPC
```
