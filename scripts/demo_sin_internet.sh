#!/usr/bin/env bash
# Radar de Decisiones en MODO_DEMO: la app nunca llama a la API (solo caché o plantilla).
# Se usa si el wifi de la sala falla o la API va lenta. Dueño: Julian.
# Uso, desde Git Bash en la raíz del repo:  bash scripts/demo_sin_internet.sh
set -e
cd "$(dirname "$0")/.."
# shellcheck disable=SC1091
source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate
echo
echo "  MODO_DEMO encendido: las explicaciones salen del caché o de la plantilla, sin internet."
echo
MODO_DEMO=1 streamlit run app.py
