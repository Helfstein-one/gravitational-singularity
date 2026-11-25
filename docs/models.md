# 🧠 Matriz de 12 Modelos Locais no Apple Silicon

Como transformamos um **MacBook Air de 16GB de RAM** em uma estação de trabalho agêntica autônoma sem estourar a memória unificada nem depender de APIs pagas para tarefas mecânicas.

---

## 1. Gráficos Comparativos do Ecossistema Local

<div align="center">
  <a href="../assets/vram_footprint.svg">
    <img src="../assets/vram_footprint.svg" alt="Pegada de Memória Unificada dos Modelos Locais" width="100%" style="border-radius: 12px; margin: 15px 0; border: 1px solid #30363d;" />
  </a>
  <p><em>Figura 1: Pegada de Memória Unificada dos Modelos Locais vs. Teto Seguro de 8.5 GB VRAM no Apple Silicon M4. [<a href="../assets/vram_footprint.svg">Abrir SVG Vetorial em Alta Resolução</a>]</em></p>
</div>

### A. Alocação de Memória Unificada (VRAM em GB)
O maior modelo (`qwen2.5-coder:7b`) consome 4.7 GB. Como o Ollama carrega e descarrega sob demanda (ou sob co-residência gerenciada pelo `InferenceOptimizer`), a máquina opera com folga térmica e sem swap de disco:

```mermaid
xychart-beta
    title "Pegada de Memória Unificada (VRAM em GB)"
    x-axis ["nomic-embed", "mau-c", "deepseek-1.5b", "llama-1b", "granite-2b", "smollm-1.7b", "qwen-3b", "hermes-3b", "qwen-7b"]
    y-axis "VRAM (GB)" 0 --> 5
    bar [0.27, 0.41, 1.10, 1.23, 1.60, 1.70, 1.88, 2.00, 4.70]
```

### B. Velocidade de Inferência por Modelo (Metal GPU / Apple Silicon M4)
Velocidade empírica medida em geração contínua via benchmark live no Ollama (`eval_count / eval_duration`):

```mermaid
xychart-beta
    title "Velocidade de Inferência Local Medida no Apple Silicon M4 (Tokens / Segundo)"
    x-axis ["deepseek-1.5b", "smollm-1.7b", "qwen-3b", "hermes-3b", "qwen-7b"]
    y-axis "Tokens / s" 0 --> 90
    bar [78, 50, 43, 35, 21]
```

> [!NOTE]
> Valores medidos em hardware real (Apple Silicon M4 16GB, Ollama Metal v0.40.6). O `deepseek-r1:1.5b` lidera com 77.7 tok/s e TTFT de 49.8ms; o `qwen2.5-coder:7b` entrega 20.8 tok/s mantendo precisão de código sem estouro de VRAM (4.43 GB).

### C. Volume de Tokens Offloaded por Modelo (Produção)
Distribuição de tokens resolvidos localmente com custo zero de nuvem:

```mermaid
xychart-beta
    title "Volume de Tokens Poupados por Modelo Local"
    x-axis ["nomic-embed", "deepseek-r1", "smollm2", "qwen-coder-3b", "hermes3", "mau-llm-c", "granite-dense"]
    y-axis "Tokens Salvos" 0 --> 35000
    bar [31872, 18400, 16200, 14250, 11800, 9200, 8500]
```

---

## 2. Dicionário Operacional dos 12 Modelos Locais

| # | Modelo | Tamanho (VRAM) | Categoria | Papel Específico no Antigravity |
| :-: | :--- | :---: | :---: | :--- |
| **1** | **`qwen2.5-coder:7b`** | 4.43 GB | Code Generation | **Builder Elite:** Refatorações pesadas, geração de módulos inteiros, arquitetura de classes e algoritmos complexos a ~21 tok/s. |
| **2** | **`qwen2.5-coder:3b`** | 1.89 GB | Fast Coding | **Builder Ágil:** Esboço de funções utilitárias, testes unitários, scripts rápidos e conversão de schemas a ~43 tok/s. |
| **3** | **`smollm2:1.7b`** | 0.98 GB | Micro-Coding / Triage | **Micro-Worker / Fast Coder:** Resolução instantânea de docstrings, tipagem, formatação, regex e correções pontuais a ~50 tok/s. |
| **4** | **`deepseek-r1:1.5b`** | 0.91 GB | Reasoning / CoT | **Skeptic Auditor:** Raciocínio com cadeia de pensamento estruturada para extrair schemas JSON estritos e validar lógica adversarial a ~78 tok/s. |
| **5** | **`nomic-embed-text`** | 0.31 GB | Vector Embeddings | **Scout / RAG:** Gera vetores de 768 dimensões com janela de 8192 tokens para busca semântica AST cirúrgica no código. |
| **6** | **`hermes3:3b`** | 2.00 GB | Agentic / Function Calling | **Scribe Epistêmico:** Destila históricos de conversas de +2M tokens em resumos de estado de <500 tokens (`session_state.md`). |
| **7** | **`granite3.1-moe:3b`** | 1.40 GB | Mixture-of-Experts | **Tool Master / Function Caller:** Roteamento agêntico e resolução nativa de tool-calls com alta velocidade. |
| **8** | **`granite3-dense:2b`** | 1.60 GB | Enterprise Reasoning | **RAG Reasoner:** Analisa blocos recuperados do repositório e sintetiza contexto para o orquestrador. |
| **9** | **`mau-llm-1.0-c`** | 0.41 GB | Micro-Coder | **Linter & Formatter:** Micro-tarefas de formatação instantânea, correção de indentação e pequenas correções de estilo. |
| **10** | **`mau-llm-1.0-r`** | 0.41 GB | Micro-Reasoning | **Fast Checker:** Validações booleanas e checagens lógicas rápidas de baixa latência (<15ms). |
| **11** | **`mau-llm-1.0-g`** | 0.41 GB | Micro-General | **Triage Agent:** Triagem de intenção do usuário e roteamento de comandos. |
| **12** | **`llama3.2:1b`** | 1.23 GB | General NLP | **Assistant Geral:** Resumos rápidos de documentação e redação de mensagens convencionais de commit. |

---

## 3. Modelos Locais Adicionais Homologados (Ollama & Memória M4)

Avaliamos e homologamos novos modelos locais de código aberto para expansão do enxame sem violar o teto estrito de **8.5 GB VRAM** no Apple Silicon M4 (16 GB RAM):

| Modelo Ollama | Parâmetros / VRAM | Velocidade (M4) | Vocação Cognitiva & Operacional |
| :--- | :---: | :---: | :--- |
| **`phi4-mini:3.8b`** | 3.8B · **2.50 GB** | **~42 tok/s** | **Lógica Simbólica & Invariantes:** Líder de sua categoria em raciocínio formal e verificação matemática. Valida pré-condições e invariantes de algoritmos antes do commit. |
| **`starcoder2:3b`** | 3.0B · **2.10 GB** | **~45 tok/s** | **Fill-In-The-Middle (FIM) Cirúrgico:** Projetado especificamente para completar código entre prefixo e sufixo. Perfeito para patches cirúrgicos mono-linha (`Ponytail`) sem regenerar funções inteiras. |
| **`granite3.1-dense:2b`** | 2.0B · **1.60 GB** | **~50 tok/s** | **Geração de Testes & QA (Apache 2.0):** Modelo enterprise da IBM focado em cobertura de testes unitários, asserções de borda com `pytest` e checagem de contratos de API. |
| **`qwen2.5:1.5b-instruct`** | 1.5B · **1.20 GB** | **~80 tok/s** | **Tool-Calling & Parser BNF Ultrarrápido:** Interpreta intenções de voz/texto e extrai parâmetros estritos JSON via gramática BNF em menos de 15ms. |

---

## 4. Perfis de Time-Slicing Neural (Co-residência Segura)

Para manter a máquina com mais de 10 GB de RAM livre para o macOS e ferramentas de desenvolvimento, o orquestrador opera por perfis modais:

```mermaid
graph TD
    subgraph ProfileA ["Perfil 1: Síntese & Auditoria (5.34 GB VRAM)"]
        Q7B["qwen2.5-coder:7b (4.43 GB)"] --- D15["deepseek-r1:1.5b (0.91 GB)"]
    end
    subgraph ProfileB ["Perfil 2: Lógica Formal & RAG (3.72 GB VRAM)"]
        P4["phi4-mini:3.8b (2.50 GB)"] --- D15B["deepseek-r1:1.5b (0.91 GB)"] --- NOMIC["nomic-embed (0.31 GB)"]
    end
    subgraph ProfileC ["Perfil 3: Patches FIM & Testes QA (3.70 GB VRAM)"]
        STAR["starcoder2:3b (2.10 GB)"] --- GRAN["granite3.1-dense:2b (1.60 GB)"]
    end
    subgraph ProfileD ["Perfil 4: MCP / Stdio Ultrabaixa Latência (2.18 GB VRAM)"]
        Q15["qwen2.5:1.5b (1.20 GB)"] --- SMOL["smollm2:1.7b (0.98 GB)"]
    end
```

---

## 5. Matriz SaaS dos 4 Novos Modelos Google Gemini (Camada de Nuvem Estratégica)

Quando a incerteza do problema excede o limiar local ($H > 2.8$ ou complexidade ciclomática $> 10$), o [`HybridRoutingEngine`](../src/application/hybrid_routing_engine.py) escala a requisição para a fração SaaS através do [`GeminiClientAdapter`](../src/adapters/outbound/gemini_client_adapter.py):

| Modelo Gemini SaaS | Tier Operacional | Custo / 1M Tokens | Janela de Contexto | Adequação Cognitiva no Singularity |
| :--- | :---: | :---: | :---: | :--- |
| **`gemini-2.5-pro`** | **Tier 3 (Cloud Pro)** | $1.500 / 1M | 2.000.000 tokens | **Orquestrador Central & Mente:** Planejamento macro, decomposição top-down, governança de invariantes e *Thinking Budget* adaptativo (1.024 a 32.768 tokens). |
| **`gemini-2.0-flash-thinking-exp`** | **Tier 2.5 (Flash Thinking)** | $0.150 / 1M (**-90%**) | 1.000.000 tokens | **Auditor CoT & Resolução de Deadlocks:** Raciocínio matemático formal, análise de concorrência e desempate de divergências locais sem o custo do modelo Pro. |
| **`gemini-2.5-flash`** | **Tier 2 (Cloud Flash)** | $0.100 - $0.150 / 1M (**-93%**) | 1.000.000 tokens | **Pesquisa Ampla & Subagentes Concorrentes:** Leitura rápida de documentação, busca em grandes bases de dados e síntese paralela de subagentes. |
| **`gemini-2.0-flash-lite`** | **Tier 1 (Cloud Flash-Lite)** | $0.075 / 1M (**-95%**) | 1.000.000 tokens | **Micro-Validação & Linting Ultrarrápido:** Checagens pontuais de imports, tipagem, formatações e asserções booleanas com TTFT sub-100ms. |

---

## 6. As Lições do Caso de Estudo: Por Que a Arquitetura Funciona?

1. **Especialização > Tamanho Bruto:** Um modelo de 1.5B treinado em raciocínio (`deepseek-r1`) extrai JSON mais rápido e com menos alucinações que um modelo de 70B generalista forçado via prompt.
2. **Latência de Loopback Sub-milissegundo:** Como os modelos rodam em `127.0.0.1:11434` no mesmo barramento de memória Metal, o overhead de rede é zero.
3. **Imunidade a Quedas e Custos:** Tarefas de busca de código, formatação, compressão AST e resumo de sessão funcionam 100% offline, sem gastar saldo em nuvem.
4. **SaaS Estratificado de 4 Degraus:** A fração que realmente precisa de nuvem é fracionada em 4 níveis de inteligência, evitando que tarefas triviais queimem tokens do Gemini Pro.

---

## 7. Análise de Desempenho de Baixo Nível: CPython vs Cython

* **O Gargalo Real de um Sistema Multi-Agente:** Em sistemas de orquestração agêntica, **~90% a 95% do tempo total de execução** é consumido pela inferência matricial do modelo (GPU/Metal, na faixa de 20ms a 120ms local ou 800ms em nuvem).
* **Por Que o CPython Padrão Já É Quase 100% C Nativo:**
  * O analisador sintático de código (`ast`) é implementado diretamente em C no kernel do CPython.
  * O hashing criptográfico (`hashlib`), o banco relacional de cache L2 (`sqlite3`), as expressões regulares (`re`) e o serializador (`json`) são **extensões C nativas e compiladas** da biblioteca padrão.
  * Como medido na suíte de testes do projeto, **55 testes unitários e todos os roteamentos heurísticos rodam em apenas 0.33s**.
* **O Custo Oculto do Cython:** Compilar módulos `.pyx` para `.so`/`.dylib` via Cython traria ganho de fração de microsegundo (`<0.001ms`), mas destruiria a regra de ouro de **Zero Dependências Externas** (exigindo `clang`, toolchain do Xcode e setups frágeis de compilação por plataforma).
* **Decisão Arquitetural:** Mantém-se o **CPython 3.10+ puro**, usufruindo dos módulos C nativos da Standard Library com inicialização fria instantânea (**<0.26ms**).
