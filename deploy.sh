#!/usr/bin/env bash
# deploy.sh — Despliega CHAT-O a la Raspberry Pi en un solo comando.
#
# Uso:
#   ./deploy.sh                -> push + deploy (requiere working tree limpio)
#   ./deploy.sh "feat: mensaje" -> commitea los cambios pendientes con el
#                                  mensaje, y después push + deploy
#
# Variables opcionales:
#   REMOTE_HOST=santix@raspberrypi.local (default)
#   REMOTE_DIR=/home/santix/kids-chatbot (default)
#   REMOTE_PORT=7860 (default)
set -euo pipefail

REMOTE_HOST="${REMOTE_HOST:-santix@raspberrypi.local}"
REMOTE_DIR="${REMOTE_DIR:-/home/santix/kids-chatbot}"
REMOTE_PORT="${REMOTE_PORT:-7860}"
REMOTE_URL="http://localhost:${REMOTE_PORT}"
BRANCH="$(git branch --show-current)"

# 1. Commit automático si el usuario pasó mensaje o hay cambios pendientes
if ! git status --porcelain | grep -qv '^??'; then
    changes=0
else
    changes=1
fi

if [ "$changes" -eq 1 ]; then
    if [ $# -eq 0 ]; then
        echo "ERROR: hay cambios sin commitear y no pasaste mensaje de commit." >&2
        echo "        Uso: ./deploy.sh \"feat: botonera de emojis\"" >&2
        exit 1
    fi
    echo "==> Commiteando: $1"
    git add -u
    git commit -m "$1"
fi

# 2. Push
echo "==> Push de ${BRANCH} a origin"
git push origin "${BRANCH}"

# 3. Deploy remoto: backup, pull con auto-stash, restart y healthcheck
#    Seguridad: .env (Groq key) y memoria.db quedan fuera de git — el script
#    lo verifica, hace backup de TODO (excepto venv/.git), y re-verifica que
#    siguen intactos después del deploy.
ssh "${REMOTE_HOST}" "set -euo pipefail
cd '${REMOTE_DIR}'

# Protección: si .env o memoria.db dejaran de estar ignorados, ABORTAR
git check-ignore -q .env || { echo 'ERROR: .env no está en .gitignore, abortando por seguridad' >&2; exit 1; }
git check-ignore -q memoria.db || { echo 'ERROR: memoria.db no está en .gitignore, abortando por seguridad' >&2; exit 1; }

if [ -n \"\$(git status --porcelain)\" ] && ! git diff --quiet; then
    ts=\$(date +%Y%m%d-%H%M%S)
    echo '==> Cambios locales en la Pi: backup + stash'
    rsync -a --exclude venv --exclude .git --exclude __pycache__ ./ \"\${HOME}/chat-o-backup-\${ts}/\"
    git stash push -u -m \"pre-deploy auto-stash \${ts}\"
fi

before=\$(git rev-parse HEAD)
git pull --ff-only origin '${BRANCH}'
after=\$(git rev-parse HEAD)

# 2. Verificación de seguridad: config y datos intactos tras el pull
[ -s .env ] || { echo 'ERROR: .env desapareció o quedó vacío tras el deploy' >&2; exit 1; }
[ -f memoria.db ] || echo 'AVISO: memoria.db no existe (datos en otro backend?)'

if [ \"\$before\" != \"\$after\" ]; then
    echo '==> Código actualizado, reiniciando chato'
    sudo systemctl restart chato
else
    echo '==> Sin cambios de código en la Pi'
fi

# Health check con reintentos (el service tarda unos segundos en levantar)
for i in 1 2 3 4 5 6 7 8 9 10; do
    if curl -fsS -o /dev/null '${REMOTE_URL}/health'; then
        break
    fi
    [ \$i -eq 10 ] && { echo 'ERROR: /health no respondio tras el restart' >&2; exit 1; }
    sleep 1
done
echo '==> Health check OK'
curl -fsS -o /dev/null '${REMOTE_URL}/static/app.js' && echo '==> Frontend OK'"

echo "==> Deploy completo ✔  http://${REMOTE_HOST#*@}:${REMOTE_PORT}"