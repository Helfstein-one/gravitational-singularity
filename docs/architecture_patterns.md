# 🏛️ Padrões de Arquitetura Híbrida & Otimização Cognitiva (Event Horizon)

> **Documentação de Engenharia de Software & Padrões de Mercado**  
> *Referência técnica para operação híbrida Local-First (Apple Silicon M4 16GB) + Cloud SaaS (Gemini 2.0).*

---

## 🗺️ Visão Geral da Arquitetura Híbrida

O **Event Horizon** implementa uma arquitetura híbrida de inferência contínua (*Continuous Inference Fabric*). Em vez de tratar a máquina local e a nuvem como silos desconectados, o sistema divide a cognição computacional de maneira assimétrica:

```mermaid
flowchart TD
    Prompt["Entrada / Tarefa do Desenvolvedor"] --> Gatekeeper["Guardrail & AST Bypass (Sistema 0)"]
    
    Gatekeeper --> Router{"Roteador Híbrido de Entropia & Confiança"}
    
    Router -->|"Baixa Entropia / Micro-Refatoração (>0.85 Conf)"| LocalTier["Tier 0 Local (Metal GPU / Apple Silicon)"]
    Router -->|"Alta Complexidade / Decisão Arquitetural"| CloudTier["Cloud SaaS (Gemini 2.0 Pro)"]
    
    subgraph LocalTier["Tier 0 Local (100% Custo Zero)"]
        Builder["Builder: qwen2.5-coder:7b (~21 tok/s)"]
        Skeptic["Auditor Cético: deepseek-r1:1.5b (~78 tok/s)"]
        Grammar["Constrained BNF Grammar Decoding"]
        Builder --> Grammar --> Skeptic
        Skeptic -->|Aprovado em RAM| InMemAST["Validador In-Memory AST"]
        Skeptic -->|Divergência / Incerteza| CloudTier
    end

    subgraph CloudTier["Cloud SaaS (Gemini 2.0 Pro / Flash)"]
        Planner["Planejamento Macro & Invariantes de Sistema"]
        Planner -->|Diretrizes Destiladas (<500 tok)| Builder
    end

    InMemAST --> Disk["Disco / Git Working Tree"]
```

---

## 🧩 Os 6 Padrões Arquiteturais Implementados

### 1. Roteamento por Confiança & Cascata de Tarefas (FrugalGPT & RouteLLM Pattern)
- **Princípio:** O envio direto de todas as chamadas para LLMs de fronteira no SaaS gera desperdício de mais de 80% dos tokens em tarefas triviais (formatação, renomeação de variáveis, imports, correções de sintaxe).
- **Implementação:** Um classificador determinístico de baixa latência (<2ms em RAM) avalia o McCabe Complexity Index, a contagem de arquivos e a dispersão semântica.
- **Roteamento:**
  - *Confiança >= 0.85:* Resolvido 100% no Tier 0 local.
  - *Confiança < 0.85:* Compacta o contexto via AST Skeletonizer e despacha somente o esqueleto e a questão de alto nível para o Gemini Pro.

### 2. Poda Sintática AST & Merkle Tree Diferencial (Zero-Token Leakage)
- **Princípio:** Enviar arquivos inteiros para a nuvem infla a janela de contexto e degrada o raciocínio com código imperativo irrelevante.
- **Implementação:**
  - `ast-search`: Esqueletiza classes e funções, retendo tipagens, contratos e assinaturas e podando o corpo imperativo (**>68% de economia de tokens**).
  - `AstMerkleEngine`: Calcula hashes SHA-256 criptográficos por nó de função. Se apenas um método de uma classe com 10 métodos foi alterado, os 9 irmãos são preservados no cache e apenas o método-alvo é processado (**>91% de redução de diff**).

### 3. Decodificação Restrita por Gramática BNF (Outlines / XGrammar Pattern)
- **Princípio:** Modelos locais tendem a emitir preâmbulos conversacionais (*"Com certeza! Aqui está o seu código..."*) e blocos markdown que poluem o contexto e alucinam sintaxe.
- **Implementação:** Força o motor de inferência local (Ollama/MLX) a decodificar sob gramática BNF estruturada:
  ```bnf
  <patch> ::= "(" <node_id> "," <symbol_name> "," <replacement_code> ")"
  ```
- **Resultado:** Elimina 100% do ruído textual e reduz em mais de 85% os tokens gerados pelos modelos operários.

### 4. Co-Residência Estrita de VRAM no Apple Silicon M4 (16 GB Unified Memory)
- **Restrição de Hardware:** Em máquinas com 16 GB de Unified Memory, o SO e aplicações vitais consomem 6-8 GB. O teto máximo seguro para modelos de IA sem induzir swap em disco é **8.5 GB**.
- **Topologia Alocada em Produção:**
  | Modelo | Papel Cognitivo | Pegada VRAM | Velocidade M4 (Medida) |
  | :--- | :--- | :---: | :---: |
  | `deepseek-r1:1.5b` | Auditor Cético / Red-Team | 0.91 GB | **78.05 tokens/s** |
  | `qwen2.5-coder:3b` | Micro-Tarefas & JSON | 1.88 GB | **41.78 tokens/s** |
  | `qwen2.5-coder:7b` | Builder / Type-Driven Synthesis | 4.43 GB | **20.13 tokens/s** |
  | `nomic-embed-text` | RAG Vetorial Local | 0.31 GB | Latência 535 ms |
  | **Total Ativo** | **Fábrica Local Completa** | **~4.74 GB** | **>11 GB de RAM livres** |

### 5. Loop Adversarial Local (Builder vs Skeptic) Pré-SaaS
- **Princípio:** Em vez de confiar cegamente na primeira geração de um modelo 7B, um segundo modelo especializado atua como auditor adversário localmente antes que qualquer artefato seja aplicado ou enviado para a nuvem.
- **Implementação:**
  1. `qwen2.5-coder:7b` rascunha a modificação de código sob contratos de tipo.
  2. `deepseek-r1:1.5b` roda um teste de sanidade estático e formula objeções técnicas.
  3. O `GuardrailInterceptor` valida in-memory se a árvore sintática compila sem erros (`ast.parse`).
  4. Havendo divergência conceitual insolúvel localmente, o relatório consolidado de divergência é submetido ao Gemini Pro.

### 6. Cache Epistêmico em Múltiplos Níveis (L0 / L1 / L2 WAL)
- **L0 (RAM Invariante):** Schemas de ferramentas e regras estáticas fixadas em memória (<1µs).
- **L1 (LRU RAM):** Últimos 128 chunks e representações de código recentes.
- **L2 (SQLite WAL + mmap):** Base epistêmica persistente entre sessões do IDE, garantindo prefill zero para nós de código já conhecidos.

---

## 📊 Matriz de Trade-Offs: Local vs Cloud

| Dimensão | Execução Local (Tier 0) | Nuvem SaaS (Gemini Pro) | Solução Híbrida (Event Horizon) |
| :--- | :--- | :--- | :--- |
| **Custo por Milhão de Tokens** | **$0.00** | $1.50 / M | **Redução global de ~88.5% no custo** |
| **Latência Primeiro Token (TTFT)** | **49 ms** (DeepSeek 1.5B) | 800 - 1800 ms (RTT + Network) | **49 ms para ações locais** |
| **Privacidade de Código** | 100% On-Device | Trânsito em API | **Fail-closed: código sensível não sai da máquina** |
| **Capacidade Raciocínio Macro** | Limitada a contexto local | Altíssima (Janela de 2M tokens) | **Gemini atua focado no plano macro** |
| **Resistência a Alucinações** | Validador AST em RAM | Dependente de Chain-of-Thought | **Determinismo mecânico + validação formal** |
