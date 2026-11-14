# 🚀 Guia de Início Rápido, Instalação & CLI

> **Como Replicar e Executar:** Instruções para colocar o *Gravitational Singularity* em execução no seu ambiente de trabalho (macOS Apple Silicon ou Linux).

---

## ⚡ Setup em 1 Comando (Recomendado)

O repositório inclui um script de bootstrap determinístico e idempotente:

```bash
./start-here.sh
```

### Flags Opcionais do Bootstrap
* `./start-here.sh --dry-run`: Inspeciona o ambiente, checa dependências e emite o plano sem alterar o disco.
* `./start-here.sh --no-network`: Executa em modo isolado/air-gapped sem chamadas de rede.
* `./start-here.sh --json`: Emite o diagnóstico do sistema em formato JSON para automações e CI.

---

## 📦 Instalação Canônica (Ambiente Virtual)

```bash
# 1. Clonar e entrar no repositório
git clone https://github.com/Helfstein-one/gravitational-singularity.git
cd gravitational-singularity

# 2. Criar ambiente virtual Python
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar o pacote em modo editável com ferramentas de desenvolvimento
pip install -e ".[dev]"

# 4. Validar instalação com o Doctor
singularity doctor
```

---

## 🛠️ Comandos CLI Disponíveis

| Comando | Descrição | Exemplo de Uso |
| :--- | :--- | :--- |
| `singularity doctor` | Diagnóstico completo de saúde, hardware e modelos | `singularity doctor --no-network` |
| `singularity info` | Metadados do sistema operacional e VRAM em JSON | `singularity info --json` |
| `singularity mcp` | Inicia o Servidor MCP universal sobre Stdio | `singularity mcp` |
| `ast-search` | Extração de esqueletos AST e compressão de contexto | `ast-search --help` |
| `pytest` | Execução dos 170 testes unitários e de integração | `pytest -v` |
