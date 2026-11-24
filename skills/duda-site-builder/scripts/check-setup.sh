#!/usr/bin/env bash
# Confere o ambiente para a skill duda-site-builder.
#   bash check-setup.sh          relatório completo (dependências, ferramentas, credenciais)
#   bash check-setup.sh --api    idem + testa as credenciais na Partner API da Duda
#   bash check-setup.sh --hook   modo do hook de início de sessão: só fala se faltar algo
set -uo pipefail
MODE="${1:-}"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
CRED="$HOME/.config/duda/credentials.env"
missing=()
warn=()

has_skill() { # plugin instalado (qualquer marketplace) ou skill solta em ~/.claude/skills
  local n="$1"
  [ -f "$CLAUDE_DIR/skills/$n/SKILL.md" ] && return 0
  [ -f "$CLAUDE_DIR/plugins/installed_plugins.json" ] &&
    grep -q "\"$n@" "$CLAUDE_DIR/plugins/installed_plugins.json" && return 0
  return 1
}

for s in frontend-design ui-ux-pro-max impeccable; do
  has_skill "$s" || missing+=("skill obrigatória '$s' não instalada")
done

for b in python3 node npx git; do
  command -v "$b" >/dev/null 2>&1 || missing+=("comando '$b' não encontrado")
done
python3 -c "import playwright" 2>/dev/null || warn+=("Playwright (Python) ausente: pip install playwright && python3 -m playwright install chromium")

set -a
[ -f "$CRED" ] && . "$CRED"
[ -f ./.env ] && . ./.env
set +a
for v in DUDA_API_USER DUDA_API_PASS DUDA_TOKEN; do
  [ -n "${!v:-}" ] || missing+=("credencial $v ausente (preencha $CRED; modelo em .env.example do plugin)")
done
if [ -f "$CRED" ] && [ "$(stat -c %a "$CRED" 2>/dev/null || stat -f %Lp "$CRED")" != "600" ]; then
  warn+=("permissão de $CRED deveria ser 600: chmod 600 $CRED")
fi

if [ "$MODE" = "--api" ] && [ -n "${DUDA_API_USER:-}" ]; then
  code=$(curl -s -o /dev/null -w '%{http_code}' -u "$DUDA_API_USER:$DUDA_API_PASS" \
    https://api.duda.co/api/sites/multiscreen/templates)
  [ "$code" = "200" ] && echo "Partner API: OK" || missing+=("Partner API respondeu HTTP $code (usuário/senha ou IP não liberado)")
fi

if [ "$MODE" = "--hook" ]; then
  [ ${#missing[@]} -eq 0 ] && exit 0
  echo "duda-site-builder: setup incompleto — ${missing[*]}. Veja o README em github.com/uiliw/duda-site-builder."
  exit 0
fi

for m in "${missing[@]}"; do echo "FALTA  $m"; done
for w in "${warn[@]}"; do echo "AVISO  $w"; done
[ ${#missing[@]} -eq 0 ] && echo "OK: ambiente pronto para a duda-site-builder." || exit 1
