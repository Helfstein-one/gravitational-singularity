---
name: ast-search
description: AST-based context compressor and symbol search extracting high-level interfaces, function signatures, classes, and types without loading verbose file bodies, saving >60% context tokens.
---

# AST Search & Context Compressor

**Trigger:** `always_on`

**Directives:**
1. **Never read raw multi-hundred line files**: When exploring an unfamiliar module or locating functions, invoke `ast-search <path>` instead of reading the entire file with `view_file` to reduce context consumption by 60%–85%.
2. **Query before inspecting**: Use `ast-search -q <function_name> <directory>` to locate definitions and inspect signatures, parameters, return types, and docstrings before accessing source code.
3. **Targeted viewing**: Only call `view_file` on the specific 10–30 line range containing the target function body after locating line numbers and signatures via `ast-search`.
4. **Combine with Ponytail Patching**: Use the exact signatures and structural outlines obtained from `ast-search` to construct surgical `replace_file_content` patches without speculative guessing.
5. **Multi-format flexibility**: Use `--format code` (default) for LLM context injection, `--format json` for automated tool chaining and machine extraction, and `--format tree` for quick hierarchical file inspection.

## Core Capabilities & Usage

`ast-search` is a zero-dependency high-performance AST compressor supporting Python 3 and JavaScript/TypeScript.

### 1. Generating Syntax-Valid Skeletons
To inspect a file while discarding implementation bodies:
```bash
ast-search path/to/service.py
ast-search path/to/service.ts
```
Outputs syntax-valid skeletons with bodies replaced by `...` (Python) or `{ /* ... */ }` (JS/TS), preserving decorators, imports, type annotations, and docstrings.

### 2. Searching Symbols Across Codebases
To locate all symbols matching a query name or pattern:
```bash
ast-search -q "process_batch" src/
ast-search -m query -q "UserManager" lib/
```

### 3. Controlling Docstring Verbosity
Control token overhead with `--docstrings`:
- `summary` (default): Retains the first line or sentence of docstrings.
- `full`: Retains complete docstrings.
- `none`: Strips all docstrings and comments.
```bash
ast-search -d none src/pipeline.py
```

### 4. Machine-Readable JSON Hierarchy
To extract structured symbol hierarchies for subagent pipelines:
```bash
ast-search --format json src/router.ts
```

### 5. Hierarchical ASCII Tree
To view a compact symbol tree:
```bash
ast-search --format tree src/
```

## CLI Reference

```
ast-search [-h] [-f {code,json,tree}] [-m {outline,query}] [-q QUERY]
           [-d {summary,full,none}] [-l {python,javascript,typescript}]
           [-s] [paths ...]
```

| Flag | Name | Choices / Default | Description |
|---|---|---|---|
| `<paths...>` | Positional | `None` (required) | One or more file or directory paths to compress |
| `-f`, `--format` | Format | `code` (default), `json`, `tree` | Output representation mode |
| `-m`, `--mode` | Mode | `outline` (default), `query` | Full structure outline or symbol filter mode |
| `-q`, `--query` | Query | `None` | Substring or regular expression symbol filter |
| `-d`, `--docstrings` | Docstrings | `summary` (default), `full`, `none` | Docstring retention granularity |
| `-l`, `--lang` | Language | `python`, `javascript`, `typescript` | Language override (defaults to extension) |
| `-s`, `--stats` | Stats | `False` | Prints compression reduction statistics to stderr |
| `-h`, `--help` | Help | - | Displays usage documentation and exits with code 0 |

## Token Budget Optimization

| File Size | Typical Raw Tokens | Typical AST Outline | Reduction |
|---|---|---|---|
| 50–100 lines | 800–1,500 tokens | 200–450 tokens | 65%–75% |
| 100–500 lines | 2,000–8,000 tokens | 400–1,200 tokens | 75%–85% |
| 500+ lines | 10,000+ tokens | 1,000–2,500 tokens | 80%–90% |

## Integração Event Horizon
- Em fluxos com incerteza moderada ou alta, antes de ativar `hypothesis-loop-engineer` ou propor alterações cirúrgicas, use `ast-search` para mapear os pontos de entrada e contratos de interface sem inflar o histórico de contexto.
- Combine a saída do `ast-search` com o `cognitive-meta-router` para delimitar o escopo de cada subproblema na fase Plan-and-Solve.
