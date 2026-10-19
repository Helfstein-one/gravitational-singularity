# Event Horizon - Gravitational Singularity

Operando sob a disciplina de tokens, qualidade e execução agêntica com modelos locais.

## Diretrizes de Execução
- **Brevidade Direta:** Sem introduções ou conclusões desnecessárias. Modificações e execuções diretas.
- **Patches Cirúrgicos (Ponytail):** NUNCA reescrever arquivos inteiros. Usar estritamente `replace_file_content`.
- **Validação de Sintaxe In-Memory:** Assegurada pelo hook `hook_pre_tool.py` antes de qualquer gravação em disco.

## Tiering de Modelos & Roteamento
- **Local Mac (Tier 0 - Custo Zero de Nuvem):**
  - Busca Semântica / RAG: `code-rag` (modelo `nomic-embed-text`)
  - Compressão de Contexto: `ast-search` (redução >68% em tokens de visualização)
  - Micro-tarefas / Regex / JSON: MCP `local-llm-mcp` (`deepseek-r1:1.5b` / `qwen2.5-coder:3b`)
  - Local-First Draft (Zero-Cloud): MCP `local_draft_patch` (`qwen2.5-coder:7b` + Auto-Validação AST)
  - Destilação de Sessão: `session-distiller` (`hermes3:3b`)
- **Cloud Tiers (Gemini 2.0 Dynamic Routing):**
  - `flash_lite` ($0.075 / 1M | -95% vs Pro): micro-validações, lint, lookups rápidos e checagens pontuais.
  - `flash` ($0.100 / 1M | -93% vs Pro): pesquisa ampla no repositório, leitura de documentação e subagentes concorrentes.
  - `pro` ($1.500 / 1M | Orquestrador): planejamento macro, arquitetura de múltiplos módulos e decisões críticas.
