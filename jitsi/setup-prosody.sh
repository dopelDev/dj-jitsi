#!/bin/bash
# Script para descargar mod_auth_sql si no existe

PLUGIN_DIR="./prosody-config"
AUTH_SQL_URL="https://hg.prosody.im/prosody-modules/raw-file/tip/mod_auth_sql/mod_auth_sql.lua"

mkdir -p "$PLUGIN_DIR"

if [ ! -f "$PLUGIN_DIR/mod_auth_sql.lua" ]; then
    echo "Descargando mod_auth_sql..."
    curl -o "$PLUGIN_DIR/mod_auth_sql.lua" "$AUTH_SQL_URL"
    echo "mod_auth_sql descargado"
fi
