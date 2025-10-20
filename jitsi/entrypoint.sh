#!/bin/bash
set -e

echo "Iniciando Jitsi Meet con imagen oficial..."

# Configurar variables de entorno
export JITSI_DOMAIN=${JITSI_DOMAIN:-localhost}
export PUBLIC_URL=${PUBLIC_URL:-http://localhost:8080}
export ENABLE_AUTH=${ENABLE_AUTH:-false}

# Usar el entrypoint oficial de Jitsi
exec /init

