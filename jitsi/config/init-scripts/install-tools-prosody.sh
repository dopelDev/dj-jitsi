#!/bin/bash

# Script de inicialización para Prosody en entorno Docker
# Instala herramientas básicas para desarrollo

echo "🔧 Configurando Prosody para desarrollo Docker..."

# Instalar herramientas básicas
apt-get update -qq
apt-get install -y -qq curl wget netcat-openbsd

# Verificar configuración de Prosody
if [ -f "/etc/prosody/prosody.cfg.lua" ]; then
    echo "✅ Archivo de configuración principal encontrado"
else
    echo "❌ Archivo de configuración principal no encontrado"
fi

# Verificar configuración de Jitsi Meet
if [ -f "/etc/prosody/conf.d/jitsi-meet.cfg.lua" ]; then
    echo "✅ Configuración de Jitsi Meet encontrada"
    
    # Verificar configuración de WebSocket
    if grep -q "websocket" /etc/prosody/conf.d/jitsi-meet.cfg.lua; then
        echo "✅ Configuración de WebSocket encontrada"
    else
        echo "⚠️  Configuración de WebSocket no encontrada"
    fi
else
    echo "❌ Configuración de Jitsi Meet no encontrada"
fi

# Crear directorio de logs si no existe
mkdir -p /var/log/prosody
chown prosody:prosody /var/log/prosody

echo "🎉 Configuración de Prosody para desarrollo completada"

# Mostrar información de configuración
echo ""
echo "📊 Información de configuración:"
echo "   📁 Configuración principal: /etc/prosody/prosody.cfg.lua"
echo "   📁 Configuración Jitsi: /etc/prosody/conf.d/jitsi-meet.cfg.lua"
echo "   📁 Logs: /var/log/prosody/"
echo ""
echo "🔌 Configuración de WebSocket:"
echo "   Puerto WebSocket: 5280"
echo "   Puerto BOSH: 5280"
echo "   CORS habilitado: Sí"
echo "   Entorno: Desarrollo Docker"