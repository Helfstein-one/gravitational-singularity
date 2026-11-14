#!/usr/bin/env bash
# ==============================================================================
# Gravitational Singularity: Idempotent Setup, Doctor & Local Validation
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DRY_RUN=false
NO_NETWORK=false
JSON_MODE=false

for arg in "$@"; do
    case "$arg" in
        --dry-run)
            DRY_RUN=true
            ;;
        --no-network)
            NO_NETWORK=true
            ;;
        --json)
            JSON_MODE=true
            ;;
        -h|--help)
            echo "Usage: ./start-here.sh [--dry-run] [--no-network] [--json]"
            echo "Idempotent project bootstrap, doctor diagnostic and environment validation."
            exit 0
            ;;
    esac
done

if [ "$JSON_MODE" = true ]; then
    if [ -x ".venv/bin/python" ]; then
        .venv/bin/python src/adapters/inbound/doctor_cli.py info --json $( [ "$NO_NETWORK" = true ] && echo "--no-network" )
    else
        python3 src/adapters/inbound/doctor_cli.py info --json $( [ "$NO_NETWORK" = true ] && echo "--no-network" )
    fi
    exit 0
fi

echo "=================================================================="
echo "   🌌 Bootstrapping Gravitational Singularity (Zero-Cloud Engine) "
echo "=================================================================="

# 1. Virtual Environment Bootstrap
if [ ! -d ".venv" ]; then
    if [ "$DRY_RUN" = true ]; then
        echo "[dry-run] Would create Python virtual environment at .venv"
    else
        echo "[*] Creating isolated virtual environment (.venv)..."
        python3 -m venv .venv
    fi
else
    echo "[✓] Virtual environment (.venv) already exists."
fi

# 2. Dependency Installation & Editable Linking
if [ "$DRY_RUN" = true ]; then
    echo "[dry-run] Would run pip install -e \".[dev]\" inside .venv"
else
    echo "[*] Ensuring editable installation and development tools..."
    if [ "$NO_NETWORK" = true ]; then
        .venv/bin/pip install --no-index --find-links . -e ".[dev]" 2>/dev/null || .venv/bin/pip install -e ".[dev]" || true
    else
        .venv/bin/pip install -e ".[dev]" --quiet
    fi
fi

# 3. Execute System Doctor
echo ""
if [ -x ".venv/bin/python" ]; then
    DOCTOR_CMD=".venv/bin/python src/adapters/inbound/doctor_cli.py doctor"
else
    DOCTOR_CMD="python3 src/adapters/inbound/doctor_cli.py doctor"
fi

if [ "$NO_NETWORK" = true ]; then
    DOCTOR_CMD="$DOCTOR_CMD --no-network"
fi
if [ "$DRY_RUN" = true ]; then
    DOCTOR_CMD="$DOCTOR_CMD --dry-run"
fi

$DOCTOR_CMD

echo ""
echo "[✓] Bootstrap complete. You can now activate the environment:"
echo "    source .venv/bin/activate"
echo "    ast-search --help"
echo "    pytest"
echo "=================================================================="
