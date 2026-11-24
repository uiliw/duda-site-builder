#!/usr/bin/env bash
# Sobe o MCP da Duda lendo DUDA_TOKEN de ~/.config/duda/credentials.env e/ou do .env do projeto
# (o .env do projeto sobrescreve). O token nunca fica no .mcp.json.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a
# shellcheck disable=SC1090,SC1091
[ -f "$HOME/.config/duda/credentials.env" ] && . "$HOME/.config/duda/credentials.env"
# shellcheck disable=SC1091
[ -f ./.env ] && . ./.env
set +a
: "${DUDA_TOKEN:?DUDA_TOKEN ausente: preencha ~/.config/duda/credentials.env ou o .env do projeto}"
exec npx -y mcp-remote https://mcp.duda.co/mcp --header "Authorization:${DUDA_TOKEN}"
