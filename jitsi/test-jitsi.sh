#!/bin/bash

echo "🧪 Probando Jitsi Meet en puerto 8080..."
echo "========================================"

# Función para verificar si el puerto está abierto
check_port() {
    if netstat -tuln 2>/dev/null | grep -q ":8080 "; then
        echo "✅ Puerto 8080 está abierto"
        return 0
    else
        echo "❌ Puerto 8080 no está abierto"
        return 1
    fi
}

# Función para hacer petición HTTP y verificar respuesta
test_http() {
    local url=$1
    local description=$2
    
    echo ""
    echo "🔍 $description"
    echo "URL: $url"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo "✅ Respuesta HTTP 200 - OK"
        return 0
    elif [ "$response" = "000" ]; then
        echo "❌ No se puede conectar al servidor"
        return 1
    else
        echo "⚠️  Respuesta HTTP $response"
        return 1
    fi
}

# Función para verificar contenido de la página
test_content() {
    local url=$1
    local search_term=$2
    local description=$3
    
    echo ""
    echo "🔍 $description"
    echo "Buscando: '$search_term'"
    
    content=$(curl -s "$url" 2>/dev/null)
    if echo "$content" | grep -qi "$search_term"; then
        echo "✅ Contenido encontrado: '$search_term'"
        return 0
    else
        echo "❌ Contenido no encontrado: '$search_term'"
        return 1
    fi
}

# Iniciar pruebas
echo ""
echo "1️⃣ Verificando puerto 8080..."
check_port

echo ""
echo "2️⃣ Probando servidor HTTP..."
test_http "http://localhost:8080" "Página principal de Jitsi"

echo ""
echo "3️⃣ Verificando contenido de Jitsi..."
test_content "http://localhost:8080" "jitsi" "Página contiene 'jitsi'"

echo ""
echo "4️⃣ Probando sala de prueba..."
test_http "http://localhost:8080/test-room" "Sala de prueba"

echo ""
echo "5️⃣ Verificando headers del servidor..."
echo "Headers de respuesta:"
curl -I "http://localhost:8080" 2>/dev/null | head -5

echo ""
echo "6️⃣ Probando endpoint de configuración..."
test_http "http://localhost:8080/config.js" "Archivo de configuración"

echo ""
echo "========================================"
echo "🎯 Resumen de pruebas:"
echo "- Puerto 8080: $(check_port >/dev/null 2>&1 && echo "✅ OK" || echo "❌ FALLO")"
echo "- Servidor HTTP: $(test_http "http://localhost:8080" "test" >/dev/null 2>&1 && echo "✅ OK" || echo "❌ FALLO")"
echo "- Contenido Jitsi: $(test_content "http://localhost:8080" "jitsi" "test" >/dev/null 2>&1 && echo "✅ OK" || echo "❌ FALLO")"

echo ""
echo "🚀 Para probar manualmente:"
echo "   Abrir navegador en: http://localhost:8080"
echo "   Crear sala: http://localhost:8080/mi-sala-prueba"
