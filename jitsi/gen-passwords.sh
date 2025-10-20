#!/bin/bash

# Script para generar contraseñas seguras para Jitsi Meet
# Basado en las mejores prácticas documentadas en esential.md

set -e

ENV_FILE=".env"
BACKUP_FILE=".env.bak"

echo "🔐 Generando contraseñas seguras para Jitsi Meet..."

# Crear backup del .env existente si existe
if [ -f "$ENV_FILE" ]; then
    echo "📋 Creando backup de $ENV_FILE en $BACKUP_FILE"
    cp "$ENV_FILE" "$BACKUP_FILE"
fi

# Generar contraseñas seguras usando openssl
JICOFO_COMPONENT_SECRET=$(openssl rand -hex 16)
JICOFO_AUTH_PASSWORD=$(openssl rand -hex 16)
JVB_AUTH_PASSWORD=$(openssl rand -hex 16)

echo "✅ Contraseñas generadas:"
echo "   JICOFO_COMPONENT_SECRET: ${JICOFO_COMPONENT_SECRET:0:8}..."
echo "   JICOFO_AUTH_PASSWORD: ${JICOFO_AUTH_PASSWORD:0:8}..."
echo "   JVB_AUTH_PASSWORD: ${JVB_AUTH_PASSWORD:0:8}..."

# Función para actualizar o agregar variable en .env
update_env_var() {
    local var_name="$1"
    local var_value="$2"
    
    if grep -q "^${var_name}=" "$ENV_FILE" 2>/dev/null; then
        # Variable existe, actualizarla
        sed -i "s/^${var_name}=.*/${var_name}=${var_value}/" "$ENV_FILE"
        echo "   ✓ Actualizada: $var_name"
    else
        # Variable no existe, agregarla
        echo "${var_name}=${var_value}" >> "$ENV_FILE"
        echo "   ✓ Agregada: $var_name"
    fi
}

# Actualizar o agregar las contraseñas en .env
update_env_var "JICOFO_COMPONENT_SECRET" "$JICOFO_COMPONENT_SECRET"
update_env_var "JICOFO_AUTH_PASSWORD" "$JICOFO_AUTH_PASSWORD"
update_env_var "JVB_AUTH_PASSWORD" "$JVB_AUTH_PASSWORD"

echo ""
echo "🎉 ¡Contraseñas actualizadas en $ENV_FILE!"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Revisar $ENV_FILE y personalizar dominios si es necesario"
echo "   2. Ejecutar: docker compose up -d"
echo "   3. Verificar logs: docker compose logs prosody"
echo ""
echo "⚠️  IMPORTANTE: Guarda estas contraseñas de forma segura."
echo "   Si pierdes el archivo .env, tendrás que recrear las cuentas en Prosody."
