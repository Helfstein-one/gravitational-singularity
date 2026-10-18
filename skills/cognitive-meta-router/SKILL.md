---
name: cognitive-meta-router
description: Formal cognitive execution router enforcing Plan-and-Solve task decomposition, iterative Self-Refine critique loops, and multi-tier subagent token budgeting across Antigravity agents.
---

# Cognitive Meta Router

**Trigger:** `always_on`

Roteador cognitivo central do Event Horizon para agentes Antigravity. Estabelece uma disciplina formal de execução orientada a planos, filtragem contextual profunda, auto-crítica prévia de patches e alocação econômica de tokens entre subagentes.

**Directives:**
1. **No Impulsive Code Modifications:** Nenhuma alteração de código ou criação de arquivo pode ser realizada sem antes passar pelo protocolo Plan-and-Solve quando envolver $\ge 2$ arquivos, arquitetura, refatoração ou $\ge 3$ passos.
2. **Mandatory AST Context Minimization:** Antes de inspecionar ou carregar arquivos completos de código fonte no contexto, você DEVE utilizar o utilitário `ast-search` para obter a interface e esqueleto semântico.
3. **Gated Step Execution:** Cada subproblema do plano DEVE ser verificado contra seu portão de validação (gate) antes de avançar para a próxima etapa.
4. **Self-Refine Validation Loop:** Todo patch proposto deve ser avaliado pelos 4 quadrantes do Self-Refine antes da confirmação. Máximo de 3 iterações.
5. **Strict Token Budgeting:** Ao delegar trabalho para subagentes, respeite rigorosamente os limites de chamadas de ferramenta e o tier de modelo adequado (Tier 0 local, Tier 1 flash_lite, Tier 2 flash, Tier 3 pro).

---

## Protocol A: Plan-and-Solve (PS)

O protocolo **Plan-and-Solve** tem por objetivo eliminar execuções especulativas impulsivas, transformando problemas complexos em cadeias determinísticas de subproblemas verificáveis.

### 1. Critérios de Ativação
O Plan-and-Solve deve ser ativado obrigatoriamente se qualquer condição for atendida:
- O objetivo envolve $\ge 2$ arquivos ou componentes distintos.
- A tarefa requer modificação arquitetural, criação de módulos ou refatoração.
- A sequência de passos previstos possui $\ge 3$ ações ou chamadas de ferramentas.
- O nível de incerteza da tarefa é moderado ou alto.

### 2. Contrato de Execução em 4 Fases

```text
[Phase 1: Subproblem Decomposition]
                │
                ▼
[Phase 2: Context Minimization (ast-search)]
                │
                ▼
[Phase 3: Gated Step Execution] ◄──┐
                │                  │
                ▼                  │
    [Pass Gate? Yes ──> Next Step] ┘
                │ No
                ▼
[Phase 4: Halting & Diagnostic Branching]
```

#### Fase 1: Subproblem Decomposition (Decomposição Formal)
Decomponha a solicitação em uma sequência finita e ordenada de subproblemas discretos:
$$\mathcal{S} = \{S_1, S_2, \dots, S_n\}$$
Para cada passo $S_i$, documente obrigatoriamente:
- **Goal:** Meta singular e mensurável a ser atingida.
- **Inputs:** Arquivos, dados e contexto estritamente necessários.
- **Invariant:** Pré-condições obrigatórias e pós-condição formal que deve ser verdadeira antes que o passo $S_{i+1}$ possa iniciar.
- **Verification Gate:** Comando determinístico ou asserção (ex: teste unitário, lint, compilação, verificação de saída) que valida o invariant.

#### Fase 2: Context Minimization com `ast-search`
- **Regra de Ouro:** NUNCA leia arquivos de código-fonte inteiros quando a estrutura de classes, métodos e assinaturas for suficiente.
- Execute `ast-search <arquivo>` (ou `bin/ast_extractor.py`) para extrair interfaces, tipos e assinaturas.
- Carregue via `view_file` somente o trecho específico indicado pelo esqueleto AST necessário para a edição pontual (`replace_file_content`).
- Mantenha a taxa de compressão de contexto em $\ge 60\%$.

#### Fase 3: Gated Step Execution (Execução com Portão de Validação)
- Execute as operações do passo ativo $S_i$ estritamente dentro do seu escopo declarado.
- Não realize refatorações alheias ("while I'm here").
- Imediatamente após a alteração, execute o **Verification Gate** associado a $S_i$.

#### Fase 4: Halting & Diagnostic Branching (Parada e Ramificação)
- Se o Verification Gate falhar: **PARE IMEDIATAMENTE (HALT)**. Não prossiga para $S_{i+1}$.
- Se a causa for simples ou de sintaxe: execute o ciclo **Self-Refine (Protocolo B)** sobre o patch corrente.
- Se a hipótese subjacente falhar ou houver ambiguidade sistêmica: ramifique para o `hypothesis-loop-engineer` para formulação de hipóteses discriminantes.

---

## Protocol B: Self-Refine (SR)

O protocolo **Self-Refine** garante que nenhum patch ou edição seja consolidada sem uma auto-crítica prévia estruturada, prevenindo bugs sutis, quebra de contratos e poluição de contexto.

### 1. Ciclo de Refinamento Iterativo

```text
       [Propose Candidate Patch]
                   │
                   ▼
       [Quadrant Self-Critique]
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
    [All Passed?]       [Issues Found?]
         │                   │
      Yes│                 No│ (Iteration k < 3)
         ▼                   ▼
    [Commit Patch]     [Refine Candidate Patch]
                             │
                      (If k >= 3: Escalate)
```

### 2. Matriz de Crítica em 4 Quadrantes (Critique Checklist)

| Quadrante | Foco de Avaliação | Questões de Auto-Crítica Obrigatórias |
| :--- | :--- | :--- |
| **Q1: Static / Syntax** | Sintaxe, Tipagem e Lint | - O código compila sem erros?<br>- As importações necessárias foram incluídas?<br>- Tipos estáticos e anotações estão compatíveis?<br>- Há violação de convenções de lint? |
| **Q2: Behavioral / Edge Cases** | Casos de Borda e Robustez | - Entradas vazias, nulas (`None`), coleções vazias foram testadas?<br>- Divisão por zero, overflow ou limites de coleção são tratados?<br>- Caminhos de erro disparam exceções corretas? |
| **Q3: Context / Patch Hygiene** | Ponytail Patching e Economia | - O patch é cirúrgico via `replace_file_content`?<br>- Evitou regravação desnecessária de arquivos inteiros?<br>- Removeu logs de debug temporários?<br>- Não tocou em linhas fora do escopo? |
| **Q4: Invariant Preservation** | Compatibilidade e Não-Regressão | - A interface pública preexistente continua 100% retrocompatível?<br>- O contrato de saída ou formato de dados foi preservado?<br>- Algum teste existente foi quebrado? |

### 3. Invariante de Parada (Stopping Invariants)
- **Critério de Sucesso:** O patch é aprovado sem nenhuma divergência crítica nos 4 quadrantes ($Q_1 \land Q_2 \land Q_3 \land Q_4 = \text{PASS}$).
- **Limite de Iterações:** Máximo de **3 iterações** de auto-refinamento ($k \le 3$).
- **Tratamento de Exaustão:** Caso o patch não atinja convergência em 3 iterações, interrompa a edição e acione `hypothesis-loop-engineer` ou solicite clarificação ao usuário.

---

## Protocol C: Subagent Token Budgeting (STB)

O protocolo **Subagent Token Budgeting** disciplina a delegação de tarefas a agentes secundários, limitando o consumo de tokens e impondo restrições rígidas por nível de complexidade e modelo.

### 1. Hierarquia de Modelos e Orçamento de Ferramentas (4-Tier Hierarchy)

| Tier | Identificador do Modelo | Propósito e Operações Permitidas | Limite Máximo de Ferramentas | Restrição de Saída |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 0** | `local-llm-mcp` / local Ollama | Tarefas micro: extração de JSON, formatação de código, regex, boilerplate e stubs | N/A (MCP Direto) | JSON estruturado ou snippet conciso |
| **Tier 1** | `flash_lite` | Reconhecimento inicial: verificação de status, checagem de fatos isolados, grep em arquivo único, leitura de logs | $\le 5$ chamadas | Resumo ultra-curto (1 a 3 linhas) |
| **Tier 2** | `flash` | Execução técnica: exploração de código, mapeamento de dependências, rascunho de testes, patches pontuais | $\le 10$ chamadas | Tabela markdown sintética ou patch mínimo |
| **Tier 3** | `pro` | Alto raciocínio: orquestração de swarms, decomposição Plan-and-Solve, síntese de hipóteses complexas | $\le 15$ chamadas | Decisão arquitetural ou plano consolidado |

### 2. Invariantes do Subagent Token Budgeting
1. **Persona Binding Obrigatório:** NUNCA instancie um subagente genérico. Toda invocação (`invoke_subagent` ou `send_message`) DEVE ter sua persona e escopo definidos via `persona-forge` (ex: `Recon Scout`, `Evidence Collector`, `Syntax Verifier`).
2. **Pro Model Quarantine:** O modelo `pro` NUNCA deve ser atribuído a tarefas de varredura mecânica, busca de arquivos, leitura de logs ou coleta de evidências isoladas.
3. **Hard Circuit Breaker:** Se um subagente atingir o teto de tool-calls de seu Tier sem concluir o objetivo, ele DEVE emitir um resumo parcial das evidências obtidas e retornar o controle ao orquestrador em vez de insistir em novas chamadas.
4. **Structured Delivery Schema:** Todos os subagentes devem retornar seus resultados no formato padronizado:
   ```markdown
   **Context:** [Escopo atribuído]
   **Findings:** [Evidências e arquivos verificados - máximo 5 bullets]
   **Outcome:** [PASS | FAIL | BLOCKED]
   **Handoff Artifact:** [Caminho do arquivo de relatório, se aplicável]
   ```

---

## Integração Event Horizon

O `cognitive-meta-router` opera como o middleware cognitivo entre as regras globais e as skills especializadas do Event Horizon:

| Skill / Regra Relacionada | Modo de Integração |
| :--- | :--- |
| `ast-search` | Fornece a extração semântica obrigatória da Fase 2 do Plan-and-Solve para redução de contexto $\ge 60\%$. |
| `hypothesis-loop-engineer` | Destino de escalonamento quando o portão do Plan-and-Solve falha ou o Self-Refine atinge $k=3$ sem convergência. |
| `persona-forge` | Provê os templates de persona vinculados aos Tiers do Subagent Token Budgeting. |
| `parallel-swarm-orchestrator` | Implementa a distribuição paralela das tarefas decompostas do Plan-and-Solve respeitando os Tiers de modelo. |
| `react-protocol` | Fornece a granularidade imediata de pensamento (`Thought:`) dentro de cada passo do Plan-and-Solve. |
| `spec-driven-enforcer` | Converte a decomposição do Plan-and-Solve em especificações executáveis e contratos de interface. |
| `tdd-enforcer` | Fornece os Verification Gates com testes falhando previamente antes da execução de patches. |
| `stateless-relay` | Garante que subagentes consumam artefatos em disco em vez de herdar histórico inchado de contexto. |

### Fluxo Unificado de Decisão Cognitiva

```text
Solicitação de Tarefa
        │
        ▼
[Complexidade >= 2 arquivos / refatoração / >= 3 passos?]
   ├── Sim ──> Ativar cognitive-meta-router (Plan-and-Solve)
   └── Não ──> Micro-ciclo com react-protocol / execução direta
        │
        ▼
[Extrair Contexto com ast-search (>= 60% redução)]
        │
        ▼
[Executar Subproblema Si com Modelo do Tier Apropriado]
        │
        ▼
[Submeter Patch ao Self-Refine (4 Quadrantes)]
   ├── Passou ──> Validar Gate ──> Próximo Passo
   └── Falhou ──> Refinar (k <= 3) ou Escalar para hypothesis-loop-engineer
```
