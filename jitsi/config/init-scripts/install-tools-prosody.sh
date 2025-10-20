#!/bin/bash
# Instalar herramientas de diagnóstico en contenedor prosody
# Este script se ejecuta automáticamente al iniciar el contenedor

echo "🔧 Instalando herramientas de diagnóstico en prosody..."

# Intentar con apk (Alpine Linux)
if command -v apk >/dev/null 2>&1; then
    echo "📦 Usando apk (Alpine Linux)"
    apk add --no-cache procps net-tools
    if [ $? -eq 0 ]; then
        echo "✅ procps y net-tools instalados exitosamente con apk"
        exit 0
    fi
fi

# Intentar con apt-get (Debian/Ubuntu)
if command -v apt-get >/dev/null 2>&1; then
    echo "📦 Usando apt-get (Debian/Ubuntu)"
    apt-get update && apt-get install -y procps net-tools
    if [ $? -eq 0 ]; then
        echo "✅ procps y net-tools instalados exitosamente con apt-get"
        exit 0
    fi
fi

# Si llegamos aquí, la instalación falló
echo "❌ No se pudo instalar procps y net-tools en prosody"
exit 1
