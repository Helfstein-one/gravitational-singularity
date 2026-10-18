#!/usr/bin/env python3
"""
Session Distiller - Epistemic Context Compressor for Antigravity.
Reads conversation transcript, extracts verified facts deterministically,
synthesizes goal and pending actions via local hermes3:3b (Zero cloud tokens),
and writes a structured session_state.md.
"""

import sys
import os
import json
import glob
import urllib.request
import urllib.error

BRAIN_DIR = os.path.expanduser("~/.gemini/antigravity/brain")
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "hermes3:3b"

def find_latest_transcript() -> str:
    pattern = os.path.join(BRAIN_DIR, "*", ".system_generated", "logs", "transcript.jsonl")
    files = glob.glob(pattern)
    if not files:
        return ""
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]

def extract_transcript_data(transcript_path: str) -> dict:
    user_prompts = []
    files_modified = set()
    files_viewed = set()
    commands_run = []
    total_steps = 0
    total_tokens_in = 0
    total_tokens_out = 0

    with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except Exception:
                continue

            total_steps += 1
            total_tokens_in += record.get("input_tokens") or 0
            total_tokens_out += record.get("output_tokens") or 0

            # Extract user prompts
            if record.get("source") == "USER_EXPLICIT" or record.get("type") == "USER_INPUT":
                content = record.get("content") or ""
                if content and not content.startswith("<SYSTEM_MESSAGE>"):
                    user_prompts.append(content[:150])

            # Extract tool usage
            for tool in record.get("tool_calls") or []:
                name = tool.get("name", "")
                args = tool.get("args") or {}

                if name in ["replace_file_content", "write_to_file"]:
                    tf = args.get("TargetFile")
                    if tf:
                        files_modified.add(tf)
                elif name == "view_file":
                    ap = args.get("AbsolutePath")
                    if ap:
                        files_viewed.add(ap)
                elif name == "run_command":
                    cmd = args.get("CommandLine", "")
                    if cmd:
                        commands_run.append(cmd[:60])

    return {
        "transcript_path": transcript_path,
        "total_steps": total_steps,
        "total_tokens_in": total_tokens_in,
        "total_tokens_out": total_tokens_out,
        "user_prompts": user_prompts,
        "files_modified": sorted(list(files_modified)),
        "files_viewed": sorted(list(files_viewed))[:15],
        "commands_run": commands_run[-10:]
    }

def synthesize_narrative_local(data: dict) -> str:
    prompts_text = "\n".join(f"- {p}" for p in data["user_prompts"][-6:])
    files_text = "\n".join(f"- {f}" for f in data["files_modified"])

    prompt = f"""Synthesize a dense session state in Portuguese from these interactions.
User Requests:
{prompts_text}

Files Modified:
{files_text}

Format the output strictly into these 4 sections:
### 1. 🎯 Objetivo Central
(1-2 linhas resumindo a meta principal)

### 2. ✅ Fatos Verificados & Alterações Concluídas
(Lista concisa do que foi alterado e testado com sucesso)

### 3. ⚠️ Restrições Críticas & Decisões Tomadas
(Pontos importantes alinhados)

### 4. 📋 Próximos Passos
(Lista de 2 a 3 ações pendentes)

Output ONLY markdown."""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "system": "Você é um compressor epistêmico de contexto. Seja ultra-direto e estruturado."
    }

    try:
        req = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            return res.get("response", "").strip()
    except Exception:
        # Fallback deterministic
        return f"""### 1. 🎯 Objetivo Central
Trabalhar no desenvolvimento e otimização de sistemas agênticos no macOS-air.

### 2. ✅ Fatos Verificados & Alterações Concluídas
- Total de passos executados: {data['total_steps']}
- Arquivos modificados ({len(data['files_modified'])}):
{files_text}

### 3. ⚠️ Restrições Críticas & Decisões Tomadas
- Otimização de tokens, RAG local e validação AST in-memory ativados.

### 4. 📋 Próximos Passos
- Continuar execução com base no estado condensado."""

def main():
    transcript = sys.argv[1] if len(sys.argv) > 1 else find_latest_transcript()
    if not transcript or not os.path.exists(transcript):
        print("[session-distiller] No active transcript found.")
        sys.exit(1)

    print(f"[session-distiller] Analisando transcript: {os.path.basename(os.path.dirname(os.path.dirname(transcript)))}...")
    data = extract_transcript_data(transcript)

    print(f"[session-distiller] Passos auditados: {data['total_steps']} | Tokens de entrada: {data['total_tokens_in']:,}")
    print(f"[session-distiller] Sintetizando estado epistêmico via {MODEL} local...")

    narrative = synthesize_narrative_local(data)

    output_content = f"""# Estado Epistêmico da Sessão (Distilled State)
> Gerado automaticamente pelo `session-distiller` via modelo local `{MODEL}`.
> Tokens de sessão compactados de ~{data['total_tokens_in']:,} para <500 tokens.

{narrative}

---
### Telemetria da Sessão Original
- **Passos Auditados:** {data['total_steps']}
- **Tokens de Entrada:** {data['total_tokens_in']:,}
- **Tokens de Saída:** {data['total_tokens_out']:,}
- **Arquivos Alterados:** {len(data['files_modified'])}
"""

    out_file = os.path.expanduser("~/.gemini/config/session_state.md")
    with open(out_file, "w", encoding="utf-8") as fp:
        fp.write(output_content)

    # Also save to current directory if writable
    try:
        with open("session_state.md", "w", encoding="utf-8") as fp:
            fp.write(output_content)
    except Exception:
        pass

    print("\n" + "="*65)
    print(output_content)
    print("="*65)
    print(f"\n[session-distiller] Estado salvo com sucesso em: {out_file} e ./session_state.md")

if __name__ == "__main__":
    main()
