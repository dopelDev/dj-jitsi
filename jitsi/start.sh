#!/bin/bash

echo "🚀 Iniciando Jitsi Meet..."
echo "=========================="

# Función para limpiar contenedores existentes
cleanup() {
    echo ""
    echo "🧹 Limpiando contenedores existentes..."
    docker-compose down 2>/dev/null || true
    docker container rm jitsi-meet 2>/dev/null || true
}

# Función para verificar si Docker está ejecutándose
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo "❌ Docker no está ejecutándose. Inicia Docker primero."
        exit 1
    fi
    echo "✅ Docker está ejecutándose"
}

# Función para iniciar Jitsi
start_jitsi() {
    echo ""
    echo "🐳 Iniciando contenedor de Jitsi..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo "✅ Contenedor iniciado correctamente"
    else
        echo "❌ Error al iniciar el contenedor"
        exit 1
    fi
}

# Función para esperar a que el servicio esté listo
wait_for_service() {
    echo ""
    echo "⏳ Esperando a que Jitsi esté listo..."
    
    for i in {1..30}; do
        if curl -s http://localhost:8080 >/dev/null 2>&1; then
            echo "✅ Jitsi está listo!"
            return 0
        fi
        echo "   Intento $i/30..."
        sleep 2
    done
    
    echo "❌ Timeout: Jitsi no respondió en 60 segundos"
    return 1
}

# Función para mostrar logs
show_logs() {
    echo ""
    echo "📋 Mostrando logs (últimas 20 líneas):"
    echo "======================================"
    docker-compose logs --tail=20
}

# Función para ejecutar pruebas
run_tests() {
    echo ""
    echo "🧪 Ejecutando pruebas..."
    echo "======================="
    chmod +x test-jitsi.sh
    ./test-jitsi.sh
}

# Función para mostrar información útil
show_info() {
    echo ""
    echo "📋 Información del servicio:"
    echo "============================"
    echo "🌐 URL principal: http://localhost:8080"
    echo "🏠 Crear sala: http://localhost:8080/mi-sala"
    echo "📊 Estado: $(docker-compose ps --services --filter status=running | wc -l) servicios ejecutándose"
    echo ""
    echo "🔧 Comandos útiles:"
    echo "   Ver logs: docker-compose logs -f"
    echo "   Detener: docker-compose down"
    echo "   Reiniciar: docker-compose restart"
    echo "   Probar: ./test-jitsi.sh"
}

# Ejecutar secuencia completa
main() {
    check_docker
    cleanup
    start_jitsi
    
    if wait_for_service; then
        show_logs
        run_tests
        show_info
        echo ""
        echo "🎉 ¡Jitsi Meet está funcionando en http://localhost:8080!"
    else
        echo ""
        echo "❌ Error: Jitsi no se inició correctamente"
        show_logs
        exit 1
    fi
}

# Ejecutar función principal
main
